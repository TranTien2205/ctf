# Field notes — GraphQL abuse

Written by `tools/classify_solve.py` after a flag is verified, then reviewed by a
human. Nothing here is generated from guesswork: every entry cites the solved note
and the chain card it came from.

| Status | Meaning |
|---|---|
| `proposed` | written automatically after a solve; not yet reviewed |
| `confirmed` | a human checked it against the evidence and kept it |

Promote an entry by changing its status line to `confirmed`. Delete an entry that
did not hold up, and say why in the commit message. `test/regression.py` fails if
an entry has any other status.

---

## undated · Speednet · proposed

- source note: `solved live 2026-09-30, no handout; the front-end bundle was the only source`
- chain card: `knowledge/chains/htb-speednet-graphql-dev-mutation-idor-alias-2fa-bypass.json`
- verification: verified_live — {"id": 18, "number": "HTB{...}", "amount": 400, "status": "PAID", "dueDate": "1712311200000"} read from data.invoiceHistory on the live instance with the admin token
- classified as: `web-graphql` (score 3.0, 3 signals matched)
- also matched: `web-auth-session` (2.72), `web-parser-differential` (1.04), `web-request-smuggling` (0.99)
- signals that fired: graphql

**Confirming probe that worked**

> POST /graphql {"query":"{__schema{queryType{name} mutationType{name} types{name kind}}}"}

Expected: a schema document rather than an error, which is what makes every later step cheap: the whole attack surface arrives in one read

Falsifier: introspection disabled (the field is rejected or the response carries only an error), or a schema with no development-leftover mutation and no id-taking query

**Traps recorded on this solve**

- The bundle sends the raw token as the Authorization header with NO 'Bearer ' prefix; using Bearer gets 'Not authenticated' and reads like an authorization bug rather than a client mistake.
- Calling forgotPassword after devForgotPassword regenerates the token and invalidates the one you just leaked -- take the dev token and use it immediately.
- Sequential OTP brute force trips an nginx 429 that then blocks every other request to the instance. Measure the limiter before raising concurrency; the alias batch avoids it entirely.
- The OTP is bound to its own session: your own OTP against another user's session token is refused.
- GraphQL variable nullability is strict -- RegisterInput is not RegisterInput!, and the mismatch reads as a server error.

**Blast radius**: step 5 CHANGES the admin password, so the account is altered for anyone else on the instance; record the new password. Step 6 is read-only in effect (verifyTwoFactor creates nothing) but generates volume -- alias batching is the LOW-load option, 9 requests against 10000.

- status: proposed
