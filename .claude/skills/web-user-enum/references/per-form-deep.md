# Per-form (deep) — each form's full oracle profile

## /login — the hardened headline

The most-defended form. The leak order: timing (hash short-circuit) >
side (cookie/header) > body (a code/class residual) > status (a
`?error=`). A competent developer writes a uniform message AND a dummy
hash — then the variance or a second form still leaks. `login-enum.md`.

## /register — the built-to-reveal form

The form MUST tell a user a name is taken — the leak is structural, not
accidental. `"username taken"`/`"email registered"`/`409`/an inline
`aria-invalid`. The register often has a `/check-username` AJAX call —
the direct oracle. `register-reset-enum.md`.

## /forgot-password + /reset — the send-side form

A hardened uniform `"if exists, sent"` — but the send runs only for a
real row → timing gap, a `{"emails_queued"}` field, or the send itself.
The reset TOKEN path is `web-auth-session`/`web-logic-flaw`; the
existence is this class.

## /check-username + /available — the direct oracle

`GET ?u=`/`?name=`/`?email=` → `{"available":bool}`/`{"taken":bool}`/
`{"exists":bool}`. Unauthenticated, unhardened, built for the signup
form's live-check. The cheapest oracle when it exists — one request.

## /forgot-username + /unlock + /reactivate

`"we emailed your username"`/`"account unlocked"` vs `"no such account"`/
`"no locked account"` — an exists-oracle on an often-forgotten form.

## /mfa + /2fa + /send-otp

`"code sent"` only for a real account, or `"no such account"` vs `"enter
code"`. The OTP-send is the side-effect oracle; the OTP-guess is
`web-auth-session`.

## /invite + /contact

`"that email is already a member"` — a member-check on an invite form.

## /api/* + /token + /oauth

JSON error-code/boolean; `invalid_grant` vs `invalid_client`; a
`/api/users/{id}` `200`/`404`. `api-enum.md`.

## /graphql

`userByEmail`/`checkUser`/`login` resolver typed errors — the strongest
direct oracle when the schema exposes it.

## The per-form coverage rule

Each form is a separate measurement — `register: text: taken` is a
separate finding from `login: timing: +180ms`. Coverage is per-form;
a uniform `/login` does not close a leaky `/register`.
