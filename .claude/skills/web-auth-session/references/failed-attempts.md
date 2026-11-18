# Failed attempts — the anti-patterns and why they fail

The things that look like they'd work but don't — and the recorded
negative that proves each one dead for a given target.

---

## 1. Forging without a key

The most common mistake: trying claim-edits on a token whose signature
is verified. `jwt_forge` without a valid key produces a token whose
signature is wrong — the verifier rejects it before reading claims.

**The negative**: `401`/`403`/`invalid signature` on replay. Record it —
claim-forging is dead until a key lands.

## 2. alg=none on a verifier that checks alg

`jwt_forge --alg ''` produces `...signature-stripped.` — a token with an
empty signature. Verifiers that enforce `alg` reject it.

**The negative**: `401`/`unsupported algorithm`/`signature required`.
Record: alg=none dead.

## 3. RS→HS confusion without the pubkey

The confusion needs the *server's* public key as the HMAC secret.
Guessing a key or using a different key fails.

**The negative**: `401`/`invalid signature` — pubkey unreachable or
verifier pins `alg`.

## 4. kid traversal to a file you don't control

`--kid ../../../../dev/null` works only if the verifier reads `kid` as
a path AND the file's contents are your known secret. `/dev/null` gives
empty secret → sign with `''`. Other files need their contents known.

**The negative**: `401`/`key not found`/`invalid kid` — the `kid` is
whitelisted or the file read fails.

## 5. jku to a host the server can't reach

`--jku https://you/jwks.json` works only if the server fetches the URL.
A server with egress-blocked can't reach you; a server with a `jku`
whitelist won't fetch off-list.

**The negative**: `401`/`jku not allowed`/`fetch failed`/timeout.

## 6. Replaying an expired/revoked token

A stolen token with `exp` past or a `jti` in the blocklist replays to
`401`. The forge can't fix `exp` without a key.

**The negative**: `401`/`token expired`/`token revoked` — the token is
dead; steal a fresh one.

## 7. Session fixation on an app that regenerates

`?sid=EVIL` works only if the app accepts the client-supplied id AND
doesn't regenerate on login. `session_regenerate_id()` on login kills
the planted `EVIL`.

**The negative**: after login, the `Set-Cookie` carries a *different*
id — the planted one is orphaned.

## 8. Hijack on HttpOnly+Secure+SameSite

`HttpOnly` blocks `document.cookie`; `Secure` blocks http; `SameSite`
blocks cross-site send. All three = hijack dead by cookie flags alone
(you'd need the token elsewhere — log, referer, token-in-URL).

**The negative**: `document.cookie` is empty for the session cookie;
the token never appears in a stealable location.

## 9. Reset-token prediction on a real CSPRNG

A reset token from `secrets.token_urlsafe(32)` / `SecureRandom` /
`crypto.randomBytes` is not predictable. `session_dissect` will name
`high-entropy` — prediction dead.

**The negative**: the token is 128+ bits of CSPRNG — move to unbound/
Host-header/Referer-leak.

## 10. Unbound-token on a bound token

`POST /reset {token:T_victim, email:mine}` fails when the token IS
bound — the server looks up the token, finds `victim`, ignores your
`email` field.

**The negative**: `400`/`token invalid`/`email mismatch` — the token
carries the email internally.

## 11. Mass-assign on a whitelisting endpoint

`POST /register {...,"role":"admin"}` fails when the handler picks
`{username, email, password}` explicitly — `role` never reaches the
model.

**The negative**: `GET /api/me` still shows `"role":"user"` — the
field didn't bind.

## 12. Race on a unique constraint

`race_probe --write-ack` on `/register` fails when `email` has a
`UNIQUE` constraint — the second insert gets `IntegrityError`, the
handler returns `409`/`email exists`.

**The negative**: the second registration 409s — canonical unique.

## 13. MFA-skip on a server-checked gate

Direct navigation to `/home` post-password fails when the session
carries `mfa_pending: true` and `/home` checks it → redirect to `/mfa`.

**The negative**: `302 /mfa` or `403` — the intermediate session has
no authz.

## 14. MFA falsy on a strict check

`code=""`/`null`/`false` fails on `code === stored` strict check —
falsy ≠ the stored string.

**The negative**: `401`/`invalid code` — strict comparison.

## 15. OAuth state-CSRF on a checked state

Replaying a callback with a different `state` fails when the provider
binds `state` to the initiating session.

**The negative**: `400`/`state mismatch` — bound.

## 16. Impersonation on an admin-only gate

`/su?user=admin` fails when the endpoint checks `is_admin` — a low-priv
session gets `403`.

**The negative**: `403` — the impersonation feature exists but is
properly gated.

## 17. The "endpoint exists" fallacy

`GET /admin/flag` returning `404` doesn't mean the flag isn't there —
the endpoint name may differ, or it's under `/api/`, or it's a POST.
`404` is *route-not-found*, not *flag-not-here*.

**The negative**: `404` — route wrong, not flag absent. Enumerate the
admin subtree.

## 18. The "decoded = forged" confusion

`session_dissect` DECODES a token — it shows you the claims. That is
not the same as producing a token the server accepts. Decoding is
*surface*; only a replayed forge is *impact*.

**The negative**: the decoded claims look right but the replay `401`s —
the signature is still the gate.

## 19. The "XSS = session" assumption

An XSS exists but the session cookie is `HttpOnly` — `document.cookie`
doesn't carry it. The XSS must steal something else (a token in
`localStorage`, a `fetch` response, a DOM secret).

**The negative**: `document.cookie` empty for the session name — look
for `localStorage`/token-in-page instead.

## 20. The "leak = forge" timing gap

You found `SECRET_KEY` in `.env` — but the app reloads config per
deploy, or the leaked file is stale, or it's a `.env.example` with a
placeholder. Verify the key actually signs the current token.

**The negative**: `session_dissect --try-keys` with the leaked key
fails — stale/placeholder key.

## 21. The "the bot will do it" assumption

Triggering an admin bot to log in doesn't give you its session — the
bot's session is on the bot's browser, not yours. You need the bot to
*store* or *send* the flag somewhere you can read.

**The negative**: bot logged in, flag read, but it stays in the bot's
context — the second-order store is missing.

## 22. The "negative = dead" premature close

A single `401` on one endpoint doesn't close the class — the endpoint
may be the wrong one, the token format wrong, the header wrong. The
class closes on the *falsifier*: every swapped token rejected, sessions
rebound per-request, signatures verified. One `401` is one endpoint's
verdict, not the class's.

**The negative**: record it as `refutes` on *that endpoint's* hypothesis
— then try the next mechanism, not the same one.

## 23. The "try harder" loop

After five probes in a class, the budget is spent — a sixth payload in
the same class is the Polynomial failure mode. `tools/decide.py` will
say `escalate`; the rung it names (reclassify, writeup_search,
novel_plan) is cheaper than another variant.

**The negative**: five `refutes` in the class — stop; escalate.

## 24. The "writeup = recipe" trap

A writeup says "the bug is alg-confusion" — but the writeup's target
had a reachable pubkey; yours doesn't. The writeup names the *class*,
not the *probe*. The probe must be re-derived from *your* signals.

**The negative**: the writeup's payload fails — the precondition it
relied on isn't present here. Record the class-match, re-derive.

## 25. The ledger-less re-walk

The worst failure: re-running a probe whose negative is already in
`state.json`. The ledger is the memory — `--show` it before every
class-entry, and let `decide.py` skip the dead branches.
