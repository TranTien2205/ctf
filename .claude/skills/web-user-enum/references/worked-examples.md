# Worked examples — complete passes, narrated

## Example 1: the direct-oracle app

1. `web-source-map` on the SPA bundle → `fetch('/api/check-username?u=...')`
2. `curl "$BASE/api/check-username?u=admin"` → `{"available":false}`;
   `?u=zzz-x` → `{"available":true}` — direct oracle, one request
3. the seeded list: `admin`→`false`, `service`→`false`, `backup`→`false`,
   `root`→`true`, `flag`→`false` → 4 confirmed
4. `admin:admin` on `/login` → a session → `web-auth-session` for the
   post-login. Enum's job done at the verified list.

## Example 2: the uniform SPA API, the timing gap

1. `POST /api/login` → `{"error":"invalid"}` 401 on both arms — text,
   status, JSON all identical
2. the `-sv` envelope → identical; no cookie
3. the timing baseline (N=12 interleaved): `good_med=252ms`,
   `bad_med=9ms`, `jitter=5ms` → a bcrypt oracle
4. the seeded list through the timing oracle (each name, 8 samples,
   compare medians) → `service` confirmed at ~240ms
5. `service`'s reset-token was predictable → `web-auth-session`. The
   content was equalized; the hash was not.

## Example 3: the register that leaked

1. `POST /login` — fully uniform (text/status/timing/cookies all equal)
2. `POST /register` — `"username already taken"` for `admin`, a clean
   form for `zzz` → the register oracle
3. the seeded list → `admin`, `root`, `ci` confirmed
4. a password spray (`Password1`, one per account, under the lock of 5)
   → `ci:Password1` → a session. The hardened login did not protect the
   register.

## Example 4: the throttle-bypass app

1. `POST /login` — a text oracle (`"no such user"`/`"wrong password"`)
2. but a `429` after 8 attempts — a per-IP throttle
3. `X-Forwarded-For: <rand>` per request → the `429` resets → the bypass
4. a bounded spray across the enum'd `admin`/`service`/`backup` under
   the bypass → `service:letmein` → `web-auth-session`
5. recorded: `enum: /login: text` + `throttle: per-IP at 8, bypassed via XFF`

## Example 5: the GraphQL resolver

1. `POST /graphql` — `query{userByEmail(email:"x@x.c"){id}}` → `null`
   vs `{"id":5}` — a direct oracle
2. `mutation{login}` → `"USER_NOT_FOUND"` vs `"INVALID_CREDENTIALS"` —
   a second oracle
3. `admin@corp.com` confirmed → the reset-flow attack →
   `web-auth-session`. The schema exposed both oracles.
