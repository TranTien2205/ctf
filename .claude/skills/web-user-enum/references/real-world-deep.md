# Real-world cases (deep) — the published bug history

## The canonical weakness

OWASP's `Identification and Authentication Failures` (A07 in 2021)
explicitly lists "permits automated attacks such as credential
stuffing... allows or assists with **user enumeration**" — the class is
a named, standard weakness. CWE-203 (`Observable Discrepancy`), CWE-204
(`Observable Response Discrepancy`), CWE-208 (`Observable Timing
Discrepancy`) are the three oracle channels as CWEs.

## The platform precedents

### WordPress `?author=N` and `/wp-json/wp/v2/users`

`/?author=1` redirects to `/author/admin/` revealing the username;
`/wp-json/wp/v2/users` returns a public user list — the endpoint-as-
oracle pattern, unauthenticated, on millions of sites. The classic
mass-enumeration precedent.

### Drupal `user/NAME` and the login timing

Drupal's `user/<name>` path 200/404s, and its login historically hashed
only existing users → a timing oracle. Both published, both patched
with workarounds (the timing persists in many versions).

### Django/Flask uniform-message-but-timing

Django's default `AuthenticationForm` uses a uniform `"invalid login"`
BUT hashes only on a real user → a timing oracle that persisted for
years; the fix (`UserModel().set_password` on the miss) is the
dummy-hash pattern, applied only in later versions.

### OAuth/SSO `account_not_found`

Google/Microsoft/Okta flows historically returned distinct errors for
an unregistered email vs a wrong password — a SSO-leak that enables
pre-hijacking (register the victim's email first). CVE-class for
several providers.

### The `check-email`/`taken` signup oracle

Nearly every signup form's live availability check is a public
exists-oracle — structurally intended (it must tell the user), rarely
treated as a bug, universally present.

### Laravel/Spring/Rails reset timing

`"if that account exists"` uniform messages with a send-side timing
gap — the lookup+send runs only for a real row; published for Laravel's
`Password::sendResetLink`, Spring Security, Devise.

## The CTF precedents

- the `htb-phonebook` card — an LDAP bind's typed error distinguishes
  accounts (the nearest local analogue)
- a `"no such user"` teaching challenge — the honest-error shape
- a bcrypt-timing challenge — the work-asymmetry shape
- a `check-username` CTF endpoint — the direct-oracle shape

## The pattern across the CVEs

Every published bug is one channel left unequalized — the fix is always
"make the observable identical", which is why a narrow fix (uniform
text, or a dummy hash) leaves the other channels open.
