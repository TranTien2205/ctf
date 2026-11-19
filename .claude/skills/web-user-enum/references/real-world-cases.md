# Real-world cases — the published enumeration bugs

## The classic shapes

### The verbose-login era

Early apps returned `"no such user"` / `"wrong password"` directly —
the teaching-example bug. Modern frameworks default to a uniform
`"invalid credentials"`, but the residual leaks below persist.

### Timing through bcrypt

The widely-published bug: an app that hashes only existing users leaks
via a 100-300ms gap. The fix — hash a dummy on the miss arm — is known
but rarely applied; most real apps still leak timing.

### The "check availability" endpoint

A signup form's live username-check (`/available`, `/check-username`) —
built to reveal availability — is the most common real-world direct
oracle. Unauthenticated, unhardened, `{"taken":true}`.

### The reset "if exists" that still leaks

`"If that account exists, we sent a link"` — uniform text, but the
send/lookup runs only for a real row → a timing gap, or a
`{"emails_sent":N}` field, or the send itself as the side channel.

### OAuth/SSO account-exists

`Sign in with Google` on an unlinked email → a typed `account_not_found`
/`no_account` error vs a linked-account redirect — the SSO flow leaks
existence (`web-oauth-sso`).

### The registration conflict

`"This email is already registered"` — a signup that reveals existence
is nearly universal and rarely treated as a bug, but it is a working
enumeration oracle.

## The CVE-shaped precedent

- **CVE-2018-** and OWASP's `Identification and Authentication Failures`
  — "Permits automated attacks such as credential stuffing... allows or
  assists with enumeration of valid accounts" is the canonical weakness
- Drupal/WordPress/many-CMS: `user/NAME` path or `?author=N` → a user
  profile or a redirect revealing the name
- Apache/WordPress REST `/wp-json/wp/v2/users` — a public user list,
  the endpoint-as-oracle pattern

## The CTF-shaped precedent

The `htb-phonebook` chain card — an LDAP-backed login whose typed bind
error distinguishes users — is the nearest local analogue: the
authentication backend's typed error is the oracle. Record new solves
in `../field-notes.md` to promote the class.
