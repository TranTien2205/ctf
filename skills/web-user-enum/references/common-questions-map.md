# Common questions (map) — the FAQ, cross-referenced

## "The login returns 'invalid credentials' for both — is it clean?"

No — that is ONE closed cell (`/login`:body/text). The timing, the
envelope, the send, the lock, AND the other forms (register/reset/
check/api/graphql) remain open. See `channels.md`, `falsifier-map.md`.

## "I see a 200ms timing difference on one request — oracle?"

A candidate. Jitter is 10-50ms; one request is noise. N>=8 interleaved
samples, medians not means, a jitter baseline, and `FAKE` vs `FAKE2`
must be identical. See `timing-oracle.md`, `verification-protocol.md`.

## "The app locks accounts after 5 tries — can I still enumerate?"

Yes — the lockout IS the oracle. A `423 "locked"` on a real name vs
`"invalid"` on a fake leaks `exists`. But never lock a victim's
account — use your own registered account as `KNOWN`. See
`channel-side.md`, `throttling-deep.md`.

## "There's a rate limit — is enum impossible?"

Measure the counter-key first. A per-IP limit with an `X-Forwarded-For`
reset, a per-session limit with a fresh-cookie reset, a per-endpoint
limit with an alias — each is bypassable, and the bypass is the
finding. A real per-account limit bounds the SPRAY, not the oracle —
the `423` still leaks. See `rate-limit-bypass.md`.

## "The register says 'username taken' — is that the bug?"

Yes — the register's availability check is a designed existence-oracle;
the app must tell a real user the name is taken. It is the structural,
highest-confidence oracle. See `register-reset-enum.md`.

## "How do I find the check-username endpoint?"

It is an AJAX call in the register page's JS — grep the bundle
(`web-source-map`/`bundle_miner`) for `check|available|exists|username`.
Not a visible link. See `form-surface-deep.md`, `workflow-catalogue.md`.

## "What's the difference between this and SQL injection on login?"

An `admin' OR '1'='1` that bypasses the password is `web-sqli` — it
EXTRACTS/bypasses. A `admin` that returns a different error than `zzz`
is `web-user-enum` — it measures `exists`. The injection is the
stronger primitive; the enum is the differential. See `per-boundary.md`.

## "I confirmed `admin` exists — now what?"

The enum's job is done — `admin` is a verified target. The chain moves
to `web-auth-session` (weak pw/reset/SSO), `web-idor` (a `/users/admin`
read), `web-oauth-sso` (a pre-hijack). The enum is recon; the exploit
is the neighbor. See `exploitation.md`.

## "A 429 blocked my spray — the control won?"

Not necessarily — the `429` bounds the SPRAY. But an
`X-Forwarded-For`/fresh-session/alias that resets it is the finding —
record the reset. And the `423`-on-real still leaks `exists`. See
`rate-limit-bypass-deep.md`, `negative-map.md`.

## "The app uses bcrypt — can timing still work?"

Yes — the asymmetry is `verify()` runs only for real users; bcrypt's
cost makes the gap LARGER (100-300ms), not smaller. A time-equalized
app that hashes a dummy removes the delta — then check the variance
(a fixed dummy has lower stdev). See `timing-oracle.md`.
