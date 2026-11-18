# Signed Blobs — the MAC/signature bypass paths

## The shape — serialized object inside a signed envelope

The dangerous blobs are usually signed: a Rails session cookie, a JWT
payload, a `itsdangerous` blob, an ASP.NET ViewState, a `MessageVerifier`.
The grammar is deserialization; the gate is the signature. Most CTF
deserialization bugs are really *key-management* bugs — the class only dies
when the key is truly unreachable.

## The attack ordering

```
1. identify the signing scheme (HMAC-SHA*, EdDSA, RSA, Laravel AES+HMAC,
   itsdangerous HMAC, ASP.NET machineKey, Rails secret_key_base)
2. hunt the key BEFORE touching the grammar
3. only when the key is reachable → forge the blob with the gadget inside
```

## Where the key lives — the hunt list

| Signer | Key source |
|---|---|
| Rails session | `secret_key_base` — `config/secrets.yml`, `SECRET_KEY_BASE` env, `credentials.yml.enc` + master.key, error page, default `"secret"` |
| Django signed pickle | `SECRET_KEY` — `settings.py`, env, error page DEBUG=True |
| Flask itsdangerous | `SECRET_KEY` — `app.py`, env, `config.py` — forge once, session RCE |
| Laravel cookie | `APP_KEY` — `.env`, config cache, `base64:` prefix — decrypt+re-encrypt |
| JWT | `secret`/`private key` — `.env`, config, weak-secret brute-force, `alg=none`, kid traversal, `jku`/`x5u` confusion |
| ViewState | `machineKey validationKey/decryptionKey` — `web.config`, Blacklist3r default keys |
| Node itsdangerous-like | `SECRET`/`KEY` env/config |
| ActiveSupport::MessageVerifier | `secret_key_base` derivations |

## `alg=none` — the signature-not-verified case

```json
{"alg":"none","typ":"JWT"}.{"user":"admin","serialized":"<b64 gadget>"}.
```

If the verifier accepts `alg:none` (or `Alg`/`aLG` casing), no key needed —
put the gadget in the payload directly. Always test before key-hunting.

## Key-confusion — RS256→HS256 and friends

```json
{"alg":"HS256"}   // sign with the PUBLIC key as HMAC secret
```

If the verifier does `verify(token, public_key)` without checking `alg`,
the public key becomes the HMAC secret — sign with it. Public keys leak via
`/.well-known/jwks.json`, `cert.pem`, a hardcoded pem in source.

## `kid`/`jku`/`x5u` header attacks

- `kid: ../../dev/null` → the verifier reads a file as the key → sign with
  empty/known content → forge
- `jku: http://YOU/jwks.json` → verifier fetches your JWKS → sign with your
  own key
- `x5u: http://YOU/cert.pem` → same shape
- `kid: |id` or SQLi in kid → reaches a different sink

## itsdangerous/TimestampSigner — Django/Flask family

```
value.signature[.timestamp]
```

`itsdangerous` wraps a JSON or pickle payload in HMAC. `SECRET_KEY` → forge
via `itsdangerous.URLSafeTimedSerializer(key).loads`/`dumps` locally —
mint the signed blob with your gadget inside.

## Laravel `APP_KEY` — decrypt-then-re-encrypt

Laravel cookies are AES-CBC + HMAC around a serialized value. `APP_KEY`
(base64'd in `.env`) → `openssl`/the framework's encrypter decrypts; re-encrypt
the gadget with the same key. `phpggc` has no Laravel-cookie mode — craft
the POP, then wrap with the framework's encryptor.

## The Rails `secret_key_base` → session Marshal chain

```
the cookie:  <b64 marshal>.<hmac>
forge:       Marshal.dump(gadget) → base64 → HMAC-SHA1(secret_key_base)
```

With `secret_key_base` (from `secrets.yml`, env, error page, `credentials`
master key) you mint the whole cookie — the Marshal gadget inside is the
universal-Rails-RCE graph.

## The "key is truly unreachable" falsifier — when to give up

- The key is in a secrets manager/env never reflected in source, errors,
  or another challenge primitive.
- `alg=none`/confusion/kid all blocked.
- The blob is encrypted NOT signed AND the key is unreachable — no oracle
  on the decrypt path.
- `ViewStateUserKey` bound to an attacker-unknown session id AND no MAC-off.

At that point the class is dead *for this channel* — pivot to a second-order
sink (session/job/cache write that reaches the same deserializer without a
signature) or report the signature as the blocker honestly.

## Output to record

- The signing scheme + where the key came from (path/leak/default)
- Or: which header-attack bypassed the verify (`alg=none`, `kid`, `jku`)
- The forged blob + the verbatim response proving the gadget inside ran
