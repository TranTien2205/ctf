# Per-check deep — the exhaustive check-window playbooks

The complete per-check reference: the schema, the window, the probe, the
crossed state, the close, and the framework variants for every check-then-act
letter in the alphabet.

---

## A — Uniqueness (registration, name-claim)

**Schema** — `users(email UNIQUE)`, `names(name UNIQUE)` — the check
`SELECT WHERE email` → `INSERT` is two statements when the UNIQUE is absent.

**Window** — `SELECT` → `INSERT`, possibly with `sendEmail`/`bcrypt`/ORM-validation
between.

**Probe** — burst `POST /api/register` with the *same* email; `--url-b` two
different sessions on an invite cap.

**Crossed state** — `SELECT COUNT(*) FROM users WHERE email='x'` = 2; two
accounts for one actor; an owned account on a fixed email.

**Close** — `UNIQUE(email)`, `INSERT ... ON CONFLICT`, or `INSERT` inside
`SERIALIZABLE`.

**Variants** — the invite cap (`UNIQUE(invite, user)`), the username-claim
(`UNIQUE(name)`), the seat (`UNIQUE(event, seat)`).

## B — Balance (debit, transfer, convert)

**Schema** — `accounts(balance DECIMAL)` — `SELECT balance` → `if >= amt` →
`UPDATE balance - amt`.

**Window** — `SELECT` → `UPDATE`, often with a fee calc / currency convert
between.

**Probe** — burst `POST /api/withdraw` `amt=full`; `--url-b` two transfers on a
joint balance.

**Crossed state** — `balance = -amt` (floor is 0); a doubled spend on a shared
balance.

**Close** — `UPDATE ... WHERE balance >= amt` + rowcount; `FOR UPDATE`;
`SERIALIZABLE`.

**Variants** — the transfer (two rows, one joint invariant), the convert (two
currencies, one rate read), the refund-vs-charge (`--url-b`).

## C — Single-use (coupon, redemption, claim)

**Schema** — `codes(code, used)` — `SELECT used` → `if !used` → `grant` →
`UPDATE used=1`.

**Window** — `SELECT` → `UPDATE`, with the grant (an external call) between.

**Probe** — burst `POST /api/redeem` `code=owned`.

**Crossed state** — the grant executes twice; two items/credits/claims in the
inventory.

**Close** — `UPDATE codes SET used=1 WHERE code=? AND used=0` + rowcount;
`SELECT ... FOR UPDATE`.

**Variants** — the coupon (per-user or global), the invite (uses < max), the
airdrop (`claimed` flag), the OTP (`used` + `attempts`).

## D — Limit (counter, threshold, max)

**Schema** — `posts(score)`, `likes(u,t)`, `attempts` — `SELECT count` →
`if < max` → `++`.

**Window** — `SELECT` → `++`, with an `INSERT`/`UPDATE` between.

**Probe** — burst `POST /api/vote` `> cap+2`; `--url-b` two joins on a team cap.

**Crossed state** — `count > cap`; a vote counted twice for one voter; an
over-cap team.

**Close** — `UNIQUE(u,t)` (the vote), `UPDATE ... WHERE count < max` +
rowcount, a real token-bucket.

**Variants** — the vote (`UNIQUE` on the pair), the rate-limit counter, the
OTP attempts, the spin/daily (`spun_today`).

## E — (reserved for the alphabet)

## F — File-creation (upload, write, create)

**Schema** — `files(name)`, or a filesystem path — `exists`/`SELECT` →
`open`/`INSERT`.

**Window** — `exists`/`SELECT` → `save`/`INSERT`, with a path-normalise or
MIME-check between.

**Probe** — burst `POST /api/upload` same filename; a rename-loop on a tmp path.

**Crossed state** — two files with one name; an overwritten file; a
half-written file read mid-write.

**Close** — `O_EXCL`/`UNIQUE(name)`; an atomic `open(..., 'x')`; a
`SELECT ... FOR UPDATE` on the name.

## G — Claim-once (airdrop, reward, invite)

**Schema** — `users(claimed)` — `SELECT claimed` → `if !claimed` → `grant` →
`UPDATE claimed=1`.

**Window** — `SELECT` → `UPDATE`, with the grant between.

**Probe** — burst `POST /api/claim`.

**Crossed state** — the reward granted twice; two airdrops in the wallet.

**Close** — `UPDATE users SET claimed=1 WHERE id=? AND claimed=0` + rowcount.

## H — Inventory (stock, seat, quantity)

**Schema** — `items(stock)`, `seats(seat)` — `SELECT stock` → `if > 0` →
`order` → `UPDATE stock-1`.

**Window** — `SELECT` → `UPDATE`, with the order-`INSERT` between.

**Probe** — burst `POST /api/buy` `conc=stock+1`.

**Crossed state** — `stock = -1`; a seat sold twice.

**Close** — `UPDATE items SET stock=stock-1 WHERE id=? AND stock>0` + rowcount;
`UNIQUE(seat)` on the seat.

## I — (the invite — a uniqueness variant under A)

## L — Limit counter (attempts, rate, OTP tries)

**Schema** — `attempts`, `rate` — `SELECT attempts` → `if <cap` → `++` → `act`.

**Window** — `SELECT` → `++`, with the action between.

**Probe** — burst `POST /api/otp` `> cap+2` codes; burst the limited endpoint.

**Crossed state** — `attempts > cap`; more requests pass than the cap.

**Close** — `UPDATE attempts SET attempts=attempts+1 WHERE attempts<cap` +
rowcount; a real token-bucket.

## S — Session (session-count, rotation, reuse)

**Schema** — `sessions(user)` — `SELECT count(*)` → `if <1` → `INSERT` — or
the rotation `invalidate → mint → store`.

**Window** — `SELECT` → `INSERT` (the count check) or `invalidate` → `mint`
(the rotation gap).

**Probe** — burst `POST /api/login`; interleave the reset.

**Crossed state** — `Set-Cookie` ×2 under a 1-policy; two live sessions after a
rotation.

**Close** — `UNIQUE(user)` on sessions; an atomic rotate (`DELETE` + `INSERT`
in one txn).

## V — Trusted-view (verified, role, cached state)

**Schema** — `users(verified)`, `users(role)`, a cache key — `SELECT field`
→ `if trusted` → `act` on the read.

**Window** — `SELECT` → `act`, with the revoke/demote between.

**Probe** — `--url-b` `GET /api/me` + `POST /api/revoke`; `--url-b` the
action + the demote.

**Crossed state** — the action executes *as* the stale field; `verified:true`
read after the revoke.

**Close** — the check re-read inside the action's transaction; a
version-column on the view.
