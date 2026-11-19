# Account linking — the identity-match surface

Account linking is how the application decides which local account an OAuth
identity maps to. The matching field is the attack surface: when the match is
on an address the attacker can also register, the OAuth identity lands on the
attacker's account.

## The matching models

| Model | What the app matches on | The attack |
|---|---|---|
| email | the `email` claim from the IdP | register the same email locally first; the OAuth login lands on your account |
| username | the `preferred_username` or `login` claim | register the same username |
| `sub` (subject) | the IdP's unique subject identifier | usually safe — `sub` is stable and not user-controlled |
| provider+email | tuple of `iss` + `email` | safer, but a `iss` that trusts user-supplied email is still vulnerable |
| none — always creates a new account | the OAuth login always creates a fresh account | a pre-registered account is never linked; the flag lives on the unlinked one |

## The pre-registration attack

The SSOS card's shape: the bot registers a fixed account at startup. If the
registration endpoint is not idempotent — or if it races the bot's own
registerUser step — the attacker pre-registers the account with their own
password. The bot's OAuth login then lands on the attacker's account (because
the email/username matches), or the bot's registration fails silently and the
flag is written to an unreadable account.

```bash
# race the bot's registration step
for i in $(seq 1 50); do
  curl -s -X POST "$BASE/api/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"student@domain","password":"attacker_password"}' &
done
wait
# check which password won
curl -s -X POST "$BASE/api/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"student@domain","password":"attacker_password"}'
```

## The linking-direction attack

Two directions, both testable:

1. **Attacker links victim's OAuth identity** — the attacker starts an OAuth
   flow as themselves, captures the authorize URL, has the victim visit it.
   The victim's IdP session is active; the flow completes and the victim's
   OAuth identity is linked to the attacker's local account.
2. **Victim links attacker's OAuth identity** — the victim starts a flow as
   themselves; the attacker substitutes their own authorize URL. The victim's
   local account is linked to the attacker's OAuth identity; the attacker
   logs in as the victim.

The second is the more useful shape: the attacker controls the OAuth identity
(the IdP session is theirs), so the victim's local account becomes readable.

## The email-verification gap

Many IdPs return `email_verified: false` for accounts where the email was
never confirmed. If the app links on `email` without checking
`email_verified`, an attacker can register an IdP account with the victim's
email (unverified) and link into the victim's local account.

```bash
# check whether the app reads email_verified
# register an IdP account with victim's email (unverified)
# start the OAuth flow, land on the app's callback
# does the session belong to the victim's local account?
```

## Falsifier

Linking is on `sub` (the IdP's stable subject identifier), the `email` claim
is only used when `email_verified: true`, and the linking flow requires a
separate authenticated step (not automatic on first OAuth login). When this
holds, the match surface closes — move to state or redirect_uri.
