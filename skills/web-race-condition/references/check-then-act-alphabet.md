# The check-then-act alphabet — every window pattern, named

Each row is a read-then-write pair whose gap is the window, the crossed state
that proves it, and the first probe. Open the matching `per-check-*` file for
the full playbook.

---

## A — Account uniqueness (registration)

- **Read**: `SELECT id FROM users WHERE username=?` or `email=?`
- **Act**: `INSERT INTO users ...`
- **Window**: the check and the insert are two statements; with no unique
  constraint two registrations for the same name both pass the check.
- **Crossed state**: two rows share the username, or — the useful form — you
  register an account a bot will try to register later and own its credentials.
- **Probe**: hammer the register endpoint for a fixed username and confirm a
  200 before the actor that owns it reaches its own register step (SSOS).
- **Defence that closes it**: `UNIQUE(username)` constraint; the second INSERT
  raises. `INSERT ... ON CONFLICT DO NOTHING` then check the rowcount.

## B — Balance / transfer / withdraw

- **Read**: `SELECT balance FROM accounts WHERE id=?`
- **Act**: `UPDATE accounts SET balance = balance - ?` after `if balance >= amt`
- **Crossed state**: two withdrawals each for the full balance succeed;
  balance goes negative.
- **Probe**: `race_probe` on the withdraw/transfer endpoint with amount = full
  balance; count identical successes vs the serial baseline of one.
- **Defence**: `UPDATE ... SET balance = balance - ? WHERE balance >= ?`
  (single atomic statement), or `SELECT ... FOR UPDATE`.

## C — Coupon / voucher / redeem / single-use code

- **Read**: `SELECT used FROM codes WHERE code=?`
- **Act**: grant prize + `UPDATE codes SET used=1`
- **Crossed state**: the same code redeems twice — two grant operations, two
  success responses.
- **Probe**: `race_probe` on the redeem endpoint; a serial baseline gives
  200-then-400/409, a winning run gives two 200s.
- **Defence**: `UPDATE codes SET used=1 WHERE code=? AND used=0` and check
  affected rows, or a `used UNIQUE` partial index.

## D — Double-vote / like / reaction limit

- **Read**: `SELECT count(*) FROM votes WHERE user=? AND target=?`
- **Act**: `INSERT INTO votes` after `if count < max`
- **Crossed state**: vote count for one user exceeds the max (2 votes where 1
  is allowed).
- **Probe**: `race_probe` on the vote endpoint; count accepted responses.
- **Defence**: `UNIQUE(user_id, target_id)` — the race then produces a
  constraint error, not a second vote.

## E — Email / phone change + verification token (ApexSurvive)

- **Read**: generate token for the *new* address, then re-read the profile /
  send step
- **Act**: `UPDATE profile SET email=?, token=?` then `sendEmail(token)`
- **Window**: token generation and the address read are not atomic — an
  interleaved second update binds the first token to the second address.
- **Crossed state**: the token minted for address A is delivered to address B.
- **Probe**: two interleaved profile updates (A: `a@x`, B: `b@y`); observe
  which mailbox receives whose token. Needs the interleave mechanics
  (`--url-b` or a manual stall), not a burst.
- **Defence**: generate-and-send inside one transaction reading the committed
  row, or send the token only to the address read in the same statement.

## F — File / object creation race

- **Read**: `os.path.exists(path)` or `SELECT id FROM files WHERE name=?`
- **Act**: `open(path,'w')` / `INSERT`
- **Crossed state**: two files/rows where one was allowed, or a check-then-use
  path swap (classic filesystem TOCTOU).
- **Probe**: interleave two creates for the same name; watch for both
  succeeding or the second writing where the check pointed elsewhere.
- **Defence**: `O_EXCL`, unique constraint, single atomic create.

## G — Gift / airdrop / claim-once

- **Read**: `SELECT claimed FROM drops WHERE user=?`
- **Act**: transfer + `UPDATE claimed=1`
- **Crossed state**: two claim grants to one account.
- **Same shape as C** — the "code" is implicit (the account itself).

## H — Hold / reservation / inventory

- **Read**: `SELECT stock FROM items WHERE sku=?`
- **Act**: `UPDATE stock = stock - 1` after `if stock > 0`
- **Crossed state**: stock goes negative; more units sold than exist.
- **Probe**: race two purchases of the last unit.
- **Defence**: `UPDATE ... WHERE stock > 0` atomic decrement.

## I — Idempotency / dedup window

- **Read**: `SELECT id FROM ops WHERE idem_key=?`
- **Act**: perform op + `INSERT ops`
- **Crossed state**: the same idempotency key produces two effects.
- **Defence**: unique index on `idem_key`.

## J — Join / membership limit

- **Read**: `SELECT count(*) FROM members WHERE team=?`
- **Act**: `INSERT member` after `if count < cap`
- **Crossed state**: team exceeds its cap.

## K — Key exchange / pairing window

- **Read**: read partner's half-key / pending pairing record
- **Act**: write own half, compute shared secret
- **Crossed state**: an interleaved pairing binds your secret to the wrong
  partner (a cross-talk variant of E).

## L — Limit counters (rate, quota, attempts)

- **Read**: `SELECT attempts FROM counters WHERE key=?`
- **Act**: `UPDATE attempts = attempts + 1` after `if attempts < max`
- **Crossed state**: attempts accepted beyond max — OTP guess count, login
  tries, API quota.
- **Probe**: race the OTP endpoint with more concurrent attempts than the cap;
  count 200s.
- **Defence**: `UPDATE ... SET attempts = attempts + 1 WHERE attempts < max`
  atomic, then check rowcount.

## M — Money movement ordering (deposit vs withdraw)

- **Read**: balance for a withdrawal
- **Act**: debit, while a concurrent credit is mid-flight
- **Crossed state**: withdrawal validated against pre-credit balance, or a
  credit applied after a zeroing withdraw — both orders "succeed".

## N — Name/namespace claim

- **Read**: `SELECT name FROM namespaces WHERE name=?`
- **Act**: `INSERT namespace`
- **Crossed state**: two owners of one name — a per-target variant of A.

## O — OTP / verification code attempt

- **Read**: attempts counter (see L) + the code comparison itself
- **Act**: on success mark consumed / issue session
- **Crossed state**: more attempts than allowed (counter race), or two sessions
  issued for one code (consume race).
- **Probe**: burst the verify endpoint with the correct code — two `200`s with
  two session cookies is the consume race.

## P — Profile / settings TOCTOU

- **Read**: current profile row for validation
- **Act**: `UPDATE profile`
- **Crossed state**: interleaved updates each validated against the pre-state
  produce a merged state no single request was allowed to set (E's general
  form).

## Q — Queue / job claim

- **Read**: `SELECT job FROM queue WHERE status='pending' LIMIT 1`
- **Act**: `UPDATE status='running'`
- **Crossed state**: two workers run the same job (double-send, double-charge).
- **Defence**: `SELECT ... FOR UPDATE SKIP LOCKED`, or atomic
  `UPDATE ... WHERE status='pending'` claim.

## R — Referral / reward-once

- **Read**: `SELECT rewarded FROM referrals WHERE pair=?`
- **Act**: grant + mark rewarded — same shape as C/G.

## S — Session / token issue-once

- **Read**: `SELECT active_session FROM sessions WHERE user=?`
- **Act**: `INSERT session` (single-session policy)
- **Crossed state**: two live sessions where the policy allows one.

## T — Ticket / seat / slot

- **Read**: `SELECT taken FROM seats WHERE seat=?`
- **Act**: `INSERT booking`
- **Crossed state**: the same seat sold twice — H's inventory form.

## U — Upgrade / role grant once

- **Read**: `SELECT role FROM users WHERE id=?`
- **Act**: conditional `UPDATE role` — a logic gate raced past its check.

## V — Verification pending window

- **Read**: `SELECT verified FROM users WHERE id=?`
- **Act**: an action gated on `verified`, while a parallel un-verify/update is
  mid-flight — the action rides in on the stale verified state.

## W — Withdrawal-vs-deposit ordering (M's pair)

## X — Cross-request state swap (the E generalisation)

- **Read**: request-scoped object fetched after commit point
- **Act**: the commit binds fields from whichever in-flight request wrote last
- **Crossed state**: fields of A and B interleaved into one record.

## Y — Yield points in async handlers

- Every `await`, every callback boundary between the read and the commit is a
  place the runtime can schedule the other request — the language-level reason
  the window exists. See `per-framework.md`.

## Z — Zeroing the window (the defence catalogue)

- Every pattern above closes with the same three moves: one atomic statement
  that checks-and-writes, a lock held from read to commit, or a constraint that
  makes the losing write fail. When you see one of them, the window is closed —
  record the falsifier and move on.
