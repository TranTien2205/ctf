# Detection index — the whole race surface at a glance

The master index: a check, the header/record that gates it, the first probe,
the sink, and the proof. One row per detectable window.

---

## The index

| Check | Record | First probe | Sink | Proof |
|---|---|---|---|---|
| single-use code | `code.used` | `race_probe` burst on `/redeem` | the grant | 2 grants for 1 code |
| balance/withdraw | `account.balance` | `race_probe` `/withdraw` amt=full | the purchase | balance `-amt` |
| vote/like limit | `votes(user,target)` count | `race_probe` `/vote` | a threshold gate | score +2 for 1 voter |
| register uniqueness | `users.email` | burst `/register` fixed email | confused deputy | 2 rows 1 email |
| stock/seat/inventory | `items.stock` | `race_probe` `/buy` conc=stock+1 | the order | `stock=-1` |
| OTP attempt cap | `otp.attempts` | burst N>cap wrong codes | brute-force window | attempts > cap |
| OTP consume | `token.used` | burst the correct code | 2 sessions | 2 `200`s, 2 cookies |
| reset token | `resets.token` | `--concurrency 4` 2 interleaved | 2 valid tokens | both tokens work |
| profile token-cross | `profile.email` + token | `--url-b` 2 emails interleave | the mailbox | token A→address B |
| session policy | `sessions(user)` count | `race_probe` `/login` conc=4 | a 2nd live session | 2 working cookies |
| invite accept | `invites.uses` | `--url-b` 2 sessions on 1 invite | 2 memberships | both joined |
| upload/create | `files.name` | `race_probe` same filename | your file where theirs | 2 rows / overwrite |
| key rotate | `keys.current` | 2 interleaved rotations | replayable old key | old key still auths |
| oauth state | `oauth.state` | burst same code+state | 2 token exchanges | 2 grants |
| job claim | `queue.status` | 2 triggers / req vs worker | double-execute | job ran 2× |
| cart/checkout | `order.total` | `--url-b` `pay` + `cart/add` | a free item | charge ≠ order |
| vote tally | `post.score` | `race_probe` `/vote` | tally > votes | the divergence |
| rate limiter | `attempts` counter | burst past cap | more requests pass | > cap processed |
| verification flag | `user.verified` | `--url-b` `GET` + `revoke` | a stale-view ride | act on superseded |
| token rotation | `token.valid` | 2 same-token reqs | a dead token lives | old token works |
| queue dedup | `job.key` | 2 enqueues same key | 2 jobs for 1 key | duplicate work |
| team/member cap | `team.members` count | `--url-b` 2 joins | over-cap team | members > cap |
| multi-resource | `A+B` joint invariant | `--url-b` debit A + debit B | write-skew | A+B < floor |
| lock/semaphore | `lock.held` | check-held → act | a second holder | both hold |
| idempotency key | `ops.key` | 2 same-key requests | 2 effects for 1 key | duplicate effect |

## The cross-reference

| Shape | Module |
|---|---|
| balance/redeem/vote/register/otp/inventory | `per-check-balance.md` |
| token/verify/profile/session/oauth/rotate/invite | `per-check-token.md` |
| the read→write gap itself | `read-modify-write.md`, `per-mechanism.md` |
| delivery — burst, interleave, stall | `delivery-mechanics.md` |
| the serial-baseline discipline | `evidence-rules.md` |
| source greps | `detection.md`, `detection-deep.md`, `whitebox-hunt.md` |
| the alphabet | `check-then-act-alphabet.md` |
| per-route playbooks | `per-route.md` |
| verified cards | `verified-chains.md` |
| falsifiers | `falsifiers.md`, `negative-results-deep.md` |
| edge cases | `edge-cases.md`, `edge-cases-deep.md` |
| frameworks | `per-framework.md` |
| isolation levels | `database-isolation.md` |
