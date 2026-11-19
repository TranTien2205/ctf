# Real-world cases — the race shapes found in production

Named, documented race conditions and the reusable technique each one teaches.
The two verified cards live in `verified-chains.md`; this is the wider
literature the class draws from.

---

## 1. The limit-bypass single-packet attack (PortSwigger / Turbo Intruder)

The research that made the technique standard: overlapping requests delivered
in a single TCP packet / a single HTTP/2 flush win windows that a naive
`ThreadPool` flood can't.

- **Shape**: a "one vote / one transfer / one claim" check; the read→write gap
  is ms-scale.
- **Mechanic**: all last bytes of N requests in one write — the tightest start
  barrier; the requests begin processing within microseconds of each other.
- **Lesson**: delivery mechanics matter more than concurrency count. The
  tool's `--concurrency` barrier *is* the single-packet attack.
- **Reusable**: `race_probe --concurrency N --count N` — the barrier sync is
  built in.

## 2. The double-spend / overdraw (the bank-transfer classic)

- **Shape**: `SELECT balance → if balance>=amt → UPDATE balance` — the two
  statements.
- **Result**: N transfers of the full balance all succeed; the account reads
  negative.
- **Lesson**: the check and the write being separate statements is the entire
  bug — `UPDATE ... WHERE balance>=` is the one-line fix.
- **Reusable**: `per-check-balance.md` §1 — the canonical money race.

## 3. The e-commerce price race (cart-then-pay)

- **Shape**: the cart's total computed at `checkout`, the charge at `pay` — a
  `POST /cart/add` landing between them.
- **Result**: the charge is for the pre-add total; the expensive item is free.
- **Lesson**: multi-request flows carry state in a session/record — race
  across the steps, not within one endpoint.
- **Reusable**: `--url-b` — `checkout`/`pay` as A, `cart/add` as B.

## 4. The gift-card / promo stacking race

- **Shape**: "one promo per order" checked at apply-time; two promos racing
  into one order.
- **Result**: two promo discounts on one order.
- **Lesson**: the uniqueness/limit check is on the order's `promo_count` — a
  counter read → increment.

## 5. The social-media follow/like count race

- **Shape**: `SELECT count(*) WHERE user,target → INSERT vote → UPDATE tally`.
- **Result**: count +2 for one voter; the tally and the relationship table
  diverge.
- **Lesson**: a tally updated separately from the vote row is a second
  read-modify-write — race either.

## 6. The airdrop / claim-once race

- **Shape**: `SELECT claimed WHERE user → transfer → UPDATE claimed`.
- **Result**: two claim transfers to one wallet/account.
- **Lesson**: the resource is the *account's* claimed flag — race the flag,
  not the asset.

## 7. The password-reset token race

- **Shape**: invalidate-old → mint → store → send — the store and the send
  not atomic.
- **Result**: two valid tokens, or a stale token that survives the
  invalidate.
- **Lesson**: the window is between the invalidate and the store — an
  interleaved reset can keep a "dead" token alive.

## 8. The registration-uniqueness race (the SSO/confused-deputy shape)

- **Shape**: `SELECT email → INSERT` with no `UNIQUE(email)`.
- **Result**: two users sharing an email; a lookup/login maps to the wrong
  (your) row.
- **Lesson**: race the *identity* a system actor will claim — the
  highest-value primitive.
- **Verified here**: the SSOS card (`verified-chains.md` §2).

## 9. The file-upload path race (check-then-write)

- **Shape**: `exists(filename) → save(filename)` — a validate-then-use on the
  path.
- **Result**: two saves for one name, or the second write landing where the
  first's check pointed.
- **Lesson**: the TOCTOU is the re-resolution — operate on the fd, not the
  path.

## 10. The job-queue double-execute

- **Shape**: `SELECT pending → UPDATE running → execute` — no `SKIP LOCKED`.
- **Result**: the same job runs twice — two emails, two charges.
- **Lesson**: the worker's claim is check-then-act; `FOR UPDATE SKIP LOCKED`
  is the close.

## 11. The session/token rotation race

- **Shape**: `SELECT current → mint new → UPDATE → invalidate old` — the
  store and the invalidate not atomic.
- **Result**: the superseded token stays valid.
- **Lesson**: the window is between the new-token store and the old-token
  invalidate.

## 12. The rate-limit counter race

- **Shape**: `SELECT attempts → if < max → increment → allow`.
- **Result**: more attempts than the cap — OTP guess, login, API quota.
- **Lesson**: a counter race buys *more tries*, not the answer — combine with
  a weak/short code.

## 13. The auction/bid race

- **Shape**: `SELECT max(bid) → if new > max → INSERT`.
- **Result**: two bids both passing `> max` — an ambiguous winner or a
  corrupted bid-history.
- **Lesson**: the "current max" is a snapshot — the insert's own `WHERE` must
  carry the predicate.

## 14. The inventory-oversell race

- **Shape**: `SELECT stock → if > 0 → INSERT order → UPDATE stock`.
- **Result**: `stock = -1`; more units sold than exist.
- **Lesson**: `UPDATE stock = stock - 1 WHERE stock > 0` rowcount-gated is
  the atomic close.

## 15. The cross-service saga race

- **Shape**: service A validates service B's state over HTTP, then acts — the
  "transaction" spans services.
- **Result**: A acts on B's stale state — a hold that vanished, a payment
  that reversed.
- **Lesson**: there's no shared `FOR UPDATE` across services — only a
  conditional write at the data owner, a reservation, or a saga closes it.

## The case → technique table

| Case | The technique it teaches |
|---|---|
| single-packet | delivery mechanics > concurrency |
| overdraw | check-and-write in one statement |
| price race | race across flow steps |
| promo stacking | the limit counter is the window |
| follow/like | the tally is a second RMW |
| airdrop | race the claimed flag |
| reset token | invalidate↔store window |
| registration | race the actor's identity |
| upload | fd-from-check, not path |
| job queue | `SKIP LOCKED` |
| rotation | new-store↔old-invalidate |
| rate limit | a counter buys more tries |
| auction | snapshot-vs-predicate |
| inventory | atomic decrement rowcount |
| saga | conditional write at the owner |
