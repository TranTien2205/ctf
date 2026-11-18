# Signed and encoded identifiers — when the id is not really an id

An opaque identifier is not automatically a barrier. Many apps ship ids
that are signed, encrypted, encoded or hashed versions of a real key.
The IDOR question splits in two: (a) can I tamper with the carrier to
point at another object, and (b) can I mint a new carrier for an id I
chose. Either answer yes is the bug.

---

## 1. Classify the carrier first

| What it looks like | What it probably is |
|---|---|
| `VXNlcjo0Mg==` (b64, decodes to `Type:42`) | Relay global id — decode, change the 42, re-encode |
| `dGVuYW50OjE6dXNlcjo0Mg==` | composite b64 — decode shows the real fields |
| `eyJ1c2VyX2lkIjo0Mn0.signature` | signed JSON (JWT, itsdangerous, Rails signed cookie) |
| `eyJ...`.`...`.`...` three-part | JWT — `sub`, `user_id`, `jti` are the id claims |
| 24-hex | ObjectId — timestamp+random, partially predictable |
| uuid v1/v6/v7 | time-ordered — neighbour uuids guessable |
| 40-hex / 64-hex | SHA-1/SHA-256 of something — maybe of the real id |
| `id=42&sig=a1b2...` | raw id + separate signature parameter |
| `?next=/users/42&token=...` | signed URL (password reset, export, download) |
| `AAAA...==` random-looking, fixed length | encrypted id (AES-CBC/CTR of the real key) |

`tools/web/session_dissect.py` names the format for token-shaped
carriers before you touch them.

## 2. Base64 / encoding — the free win

Decode every opaque id before anything else:

```bash
echo 'VXNlcjo0Mg==' | base64 -d        # → User:42
echo 'dXNlci00Mg==' | base64 -d        # → user-42
```

If the decoded form is `Type:Int`, `Type-Int`, `{"type":"User","id":42}`
or a protobuf blob with an integer field, mutate and re-encode:

```python
import base64
for i in range(40, 46):
    print(base64.b64encode(f"User:{i}".encode()).decode())
```

Relay-style global ids are the canonical case: the same object is
fetchable by raw id (`user(id: 42)`), by global id (`node(id:
VXNlcjo0Mg==)`), and the two routes may carry different checks. Probe
BOTH.

## 3. Signed ids — where the signature lives

For `id.sig` pairs, `{"id":42,"sig":"..."}` bodies, and signed-URL
params:

**Check the signature is verified.** Change the id, keep the sig:

```
GET /users/43?sig=<sig-for-42>
```

- 200 with user 43 → signature not bound to id (or not checked) — IDOR.
- 401/403 → sig verified; move to section 4.
- 200 with user 42 → sig maps to a stored object; the id param is
  decorative — try deleting it or the sig.

**Check what is signed.** Sig over `id` only? over `id+user`? over the
whole path? A sig covering `id` but not `role` lets `{"id":42,
"role":"admin","sig":"<valid-for-id>"}` through — sig-replay plus
mass-assignment.

**Algorithm confusion.** If the carrier is a JWT: `alg:none`, RS256→
HS256 with the public key as HMAC secret, `kid` path traversal — those
live in `skills/web-auth-session/`; IDOR is the reason you want the
forge, not the technique.

## 4. Minting new signed ids

Even with verification on, the app may sign things you can influence:

- **The minting endpoint.** `/api/sign`, `/exports/new`, `/share` —
  anywhere the app returns a signed id for an object you chose. Feed it
  the victim's object id.
- **Race the signature.** Sign your own id, then flip the stored
  pointer between sign and verify (rare; see `web-race-condition`).
- **Predictable secret.** The sig is HMAC with a weak key — crack
  offline with `tools/web/session_dissect.py <token> --wordlist
  <wl>` (it handles the HMAC-candidate formats). A recovered key mints
  arbitrary signed ids.
- **Signature reuse across objects.** Some apps sign
  `hash(object_type)` not `hash(object_id)` — a sig minted for your
  invoice validates for every invoice. Swap the id, keep the sig.

## 5. Encrypted ids

Fixed-length random-looking ids that decode to a block multiple of 16
are probably AES. Signals:

- ECB: two ids sharing a 16-byte prefix decrypt to plaintexts sharing a
  prefix — sequential ids under ECB show repeated blocks.
- CBC without a MAC: flip a ciphertext byte, watch which plaintext byte
  changes in the decoded/error output — classic bit-flip into a chosen
  id. If the app decrypts `user_id` from ciphertext, flipping the last
  block's bytes walks the id up or down.
- Padding oracle: distinct responses for bad padding vs bad plaintext —
  see `crypto-symmetric-oracle` skills; the payoff is decrypting or
  re-encrypting an arbitrary `user_id` blob.

Bit-flip is the cheapest: change one byte in the penultimate block,
submit, and read which plaintext position the app reports. Two or three
flips usually land on a neighbouring id.

## 6. Hashed ids

`sha256(user_id)` as the public id: the hash of `42` is the same for
everyone. Try `hash("42")`, `hash("user:42")`, `hash("42"+salt)` where
salt appears in config/leaks, and truncated forms (first 12/16 hex).
If the app hashes without a per-object salt, enumerating ints through
the hash function regenerates the whole keyspace.

```python
import hashlib
target = "a591a6d40bf420404a011733cfb7b190..."
for i in range(1, 100000):
    if hashlib.sha256(str(i).encode()).hexdigest().startswith(target[:12]):
        print(i); break
```

MD5/SHA-1 of small ints cracks instantly — a 24-char "random" id that
is `md5("42")` enumerates the world in seconds.

## 7. Time-ordered ids (uuid v1/v6/v7, ULID, snowflake, ObjectId)

All embed a timestamp in the high bits. Given one id, neighbours are
generated by: same timestamp + decrement the low bits, or adjacent
timestamp + random tail you brute-force in a bounded window.
`uuid-analysis.md` has the byte layout and the per-format walk.

The CTF-relevant consequence: an id issued at account creation is
predictable within a time window — if the challenge seeds objects at a
known moment, generate the format for that moment and sweep the
low-entropy tail.

## 8. The composite carrier

`{"id": "VXNlcjo0Mg==", "v": 2}` — a versioned signed/encoded wrapper.
The `v` field is itself a probe: `v:1` may hit a legacy decoder without
the check. Version fields, `alg` fields, `type` fields — each is a
parser-selection knob that can route around the verifying path.

## 9. Decision table

| Carrier | First probe | If denied |
|---|---|---|
| b64 Type:id | decode → re-encode neighbour | check is real; try composite swap |
| signed id+sig | change id, keep sig | try minting endpoint, weak key |
| JWT claim | `alg:none`, claim swap | auth-session skill for the forge |
| encrypted blob | ECB pattern? CBC bit-flip | padding-oracle skill class |
| hashed int | hash the int space | per-object salt → real barrier |
| time-ordered | timestamp neighbours | uuid-analysis walk |

A signed carrier that verifies correctly and mints nothing you control
is a real negative: record the carrier, the probe, the denial, and
switch to a different carrier on the same object or a different object
type.
