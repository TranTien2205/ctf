# Case studies — the verified OAuth chains

The verified chain cards in this library. Each names the challenge, the chain,
and the lesson that transfers.

## Case 1 — SSOS (HackTheBox)

**The chain**: registration race → cookie swap → parameter confusion → flag
submit.

**The preconditions**:
- `loginSSO` ignores credentials, authorizes using the shared jar's token cookie.
- `ShouldBindJSON` (Gin) parses raw body as JSON regardless of `Content-Type`.
- SSO token cookie is `HttpOnly` with **no `SameSite`**.
- Registration endpoint allows pre-registering a fixed account.

**The chain in detail**:
1. **Race** — hammer `POST /api/register` for `student@domain` with the
   attacker's password before the bot's startup reaches its `registerUser`
   step. The bot's own registration fails; its token cookie stays on the
   attacker's account.
2. **Swap** — spray the bot's `POST /submit-url` with a `data:text/html` URL
   carrying a form that POSTs a `text/plain` JSON login to the IdP for the
   attacker's account. The `Set-Cookie` overwrites the shared jar's SSO token.
3. **Confusion** — the bot's `loginSSO` step ignores credentials and uses the
   jar's token — now the attacker's. The session becomes the attacker's
   account.
4. **Sink** — the bot submits the flag into the first assignment at startup,
   writing into the attacker's owned account. The attacker logs in and reads
   `GET /submission/:id` as the author.

**The traps**:
- The registration race alone is dead: pre-registering without the swap means
  the bot authorizes as teacher and the flag is unreachable.
- The CSRF must use `enctype=text/plain` with the JSON-name trick — a
  url-encoded form does not produce a valid JSON body.
- The internal nginx port (1337) differs from the external mapped port — the
  data URL must target the internal host:port.
- `redirect_uri` validation is strict on hostname — the `Host` header must
  include the external port for the port check to pass.
- The code exchange requires `client_secret` — the attacker cannot exchange a
  stolen code; the swap works because the bot does the exchange.
- An already-running instance is consumed — the flag is submitted once at
  startup into an account with an unknown random password.

**The lesson that transfers**: a shared cookie jar + a `loginSSO` that
ignores credentials + a `text/plain`-parsable JSON binder + a missing
`SameSite` = a cross-site session hijack. The race is the delivery; the swap
is the mechanism; the confusion is the impact.

## Case 2 — the canonical state-CSRF

**The chain**: state not bound → login-CSRF → victim's session lands on
attacker's account → attacker reads victim's data.

**The preconditions**:
- `state` is not bound to the session (or not validated at all).
- The victim has an active IdP session.
- The attacker can deliver a URL to the victim.

**The lesson that transfers**: `state` is the cheapest falsifier to test —
one callback replay names it. When it is not bound, the login-CSRF is the
cheapest exploit — no code theft, no secret, just a substituted authorize URL.

## Case 3 — the canonical redirect-interception

**The chain**: `redirect_uri` loosely validated → code delivered to attacker
→ replay against app's callback → session on victim's account.

**The preconditions**:
- `redirect_uri` is validated by prefix, suffix, substring, or wildcard.
- The `client_secret` is not needed (the code is replayed, not exchanged).

**The lesson that transfers**: `redirect_uri` validation is the second-cheapest
falsifier — one authorize request with a wrong URI names it. The interception
only works as a replay when the `redirect_uri` is strict on exchange.

## Case 4 — the canonical account-linking

**The chain**: linking on `email` → pre-register the target account → OAuth
login lands on attacker's account → read as the owner.

**The preconditions**:
- The app links on `email` or `username`, not `sub`.
- The `email_verified` claim is not enforced.
- The registration endpoint accepts any email.

**The lesson that transfers**: the linking field is the attack surface. When
it is `email` or `username`, the pre-registration race wins. When it is `sub`,
the IdP's stable identifier, the surface closes.
