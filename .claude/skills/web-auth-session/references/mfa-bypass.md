# MFA / OTP bypass — the second-factor attack surface

MFA in CTF is almost always TOTP or a numeric code. The bypass classes:
predict it, skip it, replay it, race it, confuse it, or go around it.

---

## 1. The flow map

```
login (user+pass) → /mfa (code) → session
                   ↘ backup code ↗
                   ↘ "remember device" cookie ↗
```

## 2. Skip the second factor entirely

- After the first-factor login, the app may set a **pre-MFA session** that
  already has enough privileges — request `GET /admin` right after login,
  before `/mfa` is submitted.
- Navigate directly to the post-MFA URL: the front-end guard is client-
  side, the API may not re-check.
- Add the mfa step with a **different mechanism**: `login` sets
  `mfa_pending=true` in the session; submit `{"mfa_verified":true}` or
  `{"step":2}` to a gullible endpoint.
- Drop the `mfa` field entirely from the verify POST — absent code may
  pass an `if code:` check that's skipped when the field is missing.
- Empty-string, `null`, `0`, `"000000"`, `" "` — falsy code checks.

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/api/admin" --header "Cookie: session=$PRE_MFA" \
  --evidence-regex '"role"\s*:\s*"admin"|flag\{' --evidence-kind impact \
  --on-match confirms --on-miss refutes
```

## 3. Predictable / weak code

- 4 digits → 10,000 combos; 6 → 1,000,000. If no rate limit, it's a
  bounded brute-force — run it through `id_sweep`-style loop or your
  own script with the attempt counter recorded.
- `randint(0,999999)` seeded by `time()` — two codes 1s apart reveal the
  seed.
- Code = `hash(user + day)` — compute it.
- Code returned in the send-response: `POST /send-mfa` → `{"code":"123456"}`.
- Code = last 6 of the phone number / user id.
- Code embedded in QR/`otpauth://` — decode the TOTP secret from the
  provisioning URI; PyOTP-free stdlib TOTP below.

## 4. TOTP seed extraction

The provisioning URI `otpauth://totp/x?secret=BASE32&issuer=y` leaks in:

- The enrollment response body: `{"qr":"data:image/...","secret":"JBSWY3DPEHPK3PXP"}`
- The enrollment QR itself (decode the PNG with `zbarimg`/`PIL`).
- `GET /mfa/setup` re-issuing a NEW secret on each call — old stays valid.
- A "show secret" endpoint.

Once you have the seed, mint codes locally:

```python
import hmac, hashlib, struct, base64, time
secret = base64.b32decode('JBSWY3DPEHPK3PXP')
t = int(time.time() // 30)
c = hmac.new(secret, struct.pack('>Q', t), hashlib.sha1).digest()
o = c[-1] & 0x0f
code = (struct.unpack('>I', c[o:o+4])[0] & 0x7fffffff) % 10**6
```

## 5. Race the code

`tools/web/race_probe.py` — a correct-guess code is single-use but the
"mark used" check is TOCTOU; fire the same valid code in parallel:

```bash
python3 tools/web/race_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/mfa/verify" --body '{"code":"123456"}' --write-ack
```

Same trick for a limited-attempt counter: N parallel attempts may all
pass the "<5 attempts" gate before any of them increments.

## 6. Code-vs-user confusion

- The code is checked against the user in the *body*, not the session:
  `{"code":"123456","user_id":2}` — submit a code you know for user 1,
  claim user 2.
- The verify endpoint accepts **any valid code in the system** — a code
  you minted for your own account authenticates the victim's pending
  login.
- Session carries `pending_user`; the verify checks `code` for that
  user but the *next* request uses a different identity claim.

## 7. "Remember this device" cookie

`remember_device=true` sets a long-lived cookie that skips MFA. Attack:

- The cookie is `user_id + sig` → predictable.
- The cookie is per-user but not per-device → yours unlocks everyone.
- The cookie can be **planted** in the victim's browser (subdomain) —
  then a phished first-factor login gives you the full session.

## 8. Backup codes

- Sequential (`RECOVERY-0001`...), short, or wordlist-shaped.
- The "use backup code" endpoint has a weaker rate limit than the TOTP
  one.
- Backup codes are stored plaintext in the `user` object → the IDOR/
  mass-assign chain exposes them.

## 9. SMS/email-specific

- Code sent to the address *you* registered — register a target-named
  account to get a valid-looking flow.
- SMS code in the response of the send endpoint (CTF shortcut).
- Code the same for all users at a given minute (server generates one
  global code per window).

## 10. Falsifiers

- Rate limit + single-use + bound to session + bound to user + ≥80-bit
  code → brute-force dead. Pivot to `web-logic-flaw`/`web-oauth-sso`
  or accept the class doesn't reach.
- TOTP with proper secret handling → you need the seed; if it never
  leaves the server, this class is closed.
