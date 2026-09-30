# Speednet — HackTheBox, web

Solved live on 2026-09-30 against `154.57.164.79:31103`. No handout was supplied; the
Vite bundle was the only source.

## What the target was

A React SPA over nginx 1.28.0, one API path (`/graphql`), and a mail catcher at
`/emails/` bound to the tester's own address. `tools/web/bundle_miner.py` recovered the
route list and that single API path from the minified bundle in one command.

## The chain

1. **Introspection was enabled.** One read returned the whole surface: 4 queries, 8
   mutations. Two of them decided the challenge — `userProfile(userId: Int)`, which takes
   an arbitrary id, and `devForgotPassword(email: String)` sitting beside the real
   `forgotPassword`.
2. **IDOR.** `userProfile(userId: 1)` with an ordinary account's token returned
   `admin@speednet.htb`, username `admin`, `twoFactorAuthEnabled: true`.
3. **The development leftover.** `devForgotPassword` returns the reset token in the
   response body instead of emailing it: `Dev only! Password reset token: <uuid>`. Aimed
   at the admin address it hands over the admin account's reset token.
4. **`resetPassword`** then set the admin password, and login answered
   `2FA_REQUIRED:<session uuid>`.
5. **The second factor.** Measured on the tester's own account first: the OTP is FOUR
   digits, and the app applies no attempt cap — six wrong codes left the session usable.
   But nginx rate-limits at 4-5 accepted requests per second, so 10^4 sequential attempts
   are not available, and a 30-worker attempt produced HTTP 429 that blocked every other
   request to the instance.
6. **GraphQL alias batching defeated that**, because the limiter counts HTTP requests
   while a GraphQL document can carry any number of operations. 500 aliased
   `verifyTwoFactor` mutations per request covered the keyspace in **9 requests and 35
   seconds** — fewer requests, and far less load, than the sequential attempt that failed.
7. The flag is an invoice number, read from `invoiceHistory` with the admin token.

## What cost time

- The bundle sends the raw token as `Authorization` with **no `Bearer ` prefix**. Sending
  `Bearer <token>` returns `Not authenticated`, which reads like an authorization bug
  rather than a client mistake.
- Calling `forgotPassword` right after `devForgotPassword` regenerated the token and
  invalidated the one just leaked.
- Raising concurrency before measuring the rate limiter cost a stalled instance and had to
  be stopped. Measuring first gave 4-5 req/s, and that number is what made the alias route
  obviously correct.

## Measured dead

Cross-account OTP reuse (the code is bound to its session); the reset token and the 2FA
session token are separate stores; `resendOTP` returns only `true`; empty, short, long and
zero-padded OTP shapes; JWT key recovery over 10k candidates (`session_dissect.py`).
