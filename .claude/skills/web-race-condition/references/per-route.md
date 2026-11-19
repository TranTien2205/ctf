# Per-route — the endpoint-by-endpoint playbook

Each common route shape, its window, the exact probe, and the serial-impossible
outcome that confirms it.

---

## /redeem, /coupon, /voucher, /claim, /use-code

- **Window**: `SELECT used` → grant → `UPDATE used=1`
- **Probe**: `race_probe --url $BASE/api/redeem --body '{"code":"C"}' --concurrency 20 --count 20 --baseline-count 5 --write-ack`
- **Crossed state**: 2+ `200`s for one code; 2 grants in inventory.
- **Falsifier**: `UPDATE ... WHERE used=0` rowcount gate; `409`/`400` loser.

## /withdraw, /transfer, /pay, /convert, /debit

- **Window**: `SELECT balance` → `if >=` → `UPDATE balance`
- **Probe**: `--body '{"amount":FULL}' --concurrency 10 --count 10 --baseline-count 3`
- **Crossed state**: balance `-amt`, or 2×amt extracted.
- **Falsifier**: `UPDATE ... WHERE balance >= amt` atomic.

## /vote, /like, /react, /rate, /upvote

- **Window**: `SELECT count(*) WHERE user,target` → `INSERT` → `UPDATE tally`
- **Probe**: `--body '{"post":1}' --concurrency 15 --count 15 --baseline-count 4`
- **Crossed state**: score +2 for one voter; 2 vote rows.
- **Falsifier**: `UNIQUE(user_id, target_id)`.

## /register, /signup

- **Window**: `SELECT WHERE email=?` → `INSERT`
- **Probe**: burst the fixed username, or `--url-b` two different emails.
- **Crossed state**: two rows same email; or you own a bot's fixed account.
- **Falsifier**: `UNIQUE(email)`; consumed instance (SSOS stop).

## /buy, /book, /reserve, /order, /checkout

- **Window**: `SELECT stock` → `INSERT order` → `UPDATE stock`
- **Probe**: `--concurrency = stock+1 --count same --baseline-count 3 --write-ack`
- **Crossed state**: `stock = -1`; confirmed orders > stock.
- **Falsifier**: `UPDATE ... WHERE stock > 0` rowcount; `UNIQUE(seat)`.

## /verify, /confirm, /activate, /otp, /2fa

- **Window**: `SELECT token,used` → grant → `UPDATE used`
- **Probe (cap)**: burst N > cap wrong codes — attempts past cap answered
  "invalid" not "locked".
- **Probe (consume)**: burst the correct code — 2 `200`s, 2 sessions.
- **Crossed state**: attempts > cap, or 2 grants for one token.
- **Falsifier**: atomic increment rowcount; `used=0` gate.

## /reset, /forgot, /password-reset

- **Window**: invalidate old → mint → store → `sendEmail` (outside txn)
- **Probe**: `--concurrency 4 --count 4 --baseline-count 2`; collect tokens
  from the mailbox, try each.
- **Crossed state**: 2 different valid tokens where "only latest works".
- **Falsifier**: one valid token always; invalidate inside the store txn.

## /profile, /settings, /email, /phone

- **Window**: update field → re-read → notify (ApexSurvive)
- **Probe**: `--url-b` two different values, interleave (`concurrency 2`).
- **Crossed state**: token/notification for A delivered to B.
- **Falsifier**: notify reads the committed row inside the same txn.

## /login, /session, /token

- **Window**: credential check → `SELECT session` → `INSERT` (one-session
  policy)
- **Probe**: `--concurrency 4 --count 4 --baseline-count 2`; harvest
  Set-Cookie per 200.
- **Crossed state**: 2 distinct working cookies under a 1-session policy.
- **Falsifier**: second login replaces/rejects; old cookie dead.

## /invite/accept, /join, /team/join

- **Window**: `SELECT uses` → `INSERT member` → `UPDATE uses`
- **Probe**: burst a `max_uses=1` invite with 2 sessions (`--url-b` + 2
  cookies).
- **Crossed state**: 2 memberships from one single-use invite.
- **Falsifier**: `UNIQUE(invite_code)` consumed atomically.

## /upload, /import, /create, /file

- **Window**: `exists(path/name)` → `open`/`INSERT`
- **Probe**: `--concurrency 8 --count 8 --baseline-count 3` same filename.
- **Crossed state**: 2 files/rows for one name; or a check-then-use path swap.
- **Falsifier**: `O_EXCL`/`UNIQUE(name)`; the second create errors.

## /keys/rotate, /token/refresh

- **Window**: `SELECT current` → mint → `UPDATE` + invalidate
- **Probe**: interleaved rotations; then test the superseded key.
- **Crossed state**: the *old* key still authenticates post-rotation.
- **Falsifier**: rotate+invalidate atomic; old key dead.

## /callback, /oauth/callback

- **Window**: `SELECT state` → `if match` → exchange + `DELETE state`
- **Probe**: burst the same `code`/`state` pair.
- **Crossed state**: 2 token exchanges for one code.
- **Falsifier**: provider `invalid_grant` on second exchange; state consumed
  atomically.

## /spin, /draw, /lottery, /daily, /reward

- **Window**: `SELECT claimed/spun` → grant → `UPDATE`
- **Probe**: `--concurrency N` where the reward is once-per-X.
- **Crossed state**: 2+ grants for one daily/spin allowance.
- **Falsifier**: atomic claim; a `already_claimed` loser.

## /job, /task, /queue/enqueue

- **Window**: request enqueues → worker `SELECT pending` → `UPDATE running`
- **Probe**: 2 trigger requests racing to enqueue, or a request racing the
  worker's claim.
- **Crossed state**: same job executed twice (2 emails, 2 charges).
- **Falsifier**: `FOR UPDATE SKIP LOCKED`; idempotent worker.

## /admin/grant, /promote, /role

- **Window**: `SELECT role` → `if <target` → `UPDATE role`
- **Probe**: race the grant against a revoke, or two grants.
- **Crossed state**: a role the check should have blocked.
- **Falsifier**: the role gate is a single atomic predicate.

## GET racing POST — the stale-read route

- **Window**: `GET` reads cached/snapshotted value racing the `POST` that
  changes it.
- **Probe**: `--url-b` `GET /api/x` + `POST /api/revoke-x`.
- **Crossed state**: `GET` returns pre-revoke value *after* commit.
- **Falsifier**: read path takes the write lock or a version check.

## The route → alphabet → module table

| Route family | Alphabet row | Detail module |
|---|---|---|
| redeem/coupon/claim | C, G, R | `per-check-balance.md` §2 |
| withdraw/transfer | B, M, W | `per-check-balance.md` §1 |
| vote/like | D | `per-check-balance.md` §3 |
| register/signup | A, N | `per-check-balance.md` §4 |
| buy/book/order | H, T | `per-check-balance.md` §6 |
| verify/otp | L, O | `per-check-balance.md` §5 |
| reset/forgot | token | `per-check-token.md` §2 |
| profile/settings | E, P, X | `per-check-token.md` §1 |
| login/session | S | `per-check-token.md` §4 |
| invite/join | invite | `per-check-token.md` §7 |
| upload/create | F | `per-check-balance.md` §6 |
| rotate/refresh | token | `per-check-token.md` §8 |
| oauth/callback | state | `per-check-token.md` §6 |
| spin/daily | G | `per-check-balance.md` §2 |
| job/queue | Q | `check-then-act-alphabet.md` Q |
| flow steps | multi-step | `per-boundary.md` §3 |
