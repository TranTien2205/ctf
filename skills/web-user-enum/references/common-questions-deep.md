# Common questions (deep) — the hard cases

## "The dev burned a dummy hash — is it really still enumerable?"

Almost always, yes. The dummy-hash fix equalizes the TIMING channel
(median) but not the others: the bad arm's fixed-hash has lower
variance than the good arm's per-user variable-cost hash (a variance
oracle); a `Set-Cookie`/send/lock still fires conditionally; and the
register/reset/check-username forms are rarely equalized. The fix is
narrow; the oracle space is wide.

## "Is a `200` vs `404` on `/api/users/{name}` enum or IDOR?"

Both measurements fire on one endpoint. The `200`/`404` existence
difference is `web-user-enum`; the `200` returning a user OBJECT you
should not read is `web-idor`. Record both — the enum confirms the
account; the IDOR reads it. Route the read to `web-idor`.

## "A `500` on the bad-user path — is that an oracle?"

A repeatable user-dependent `500` IS a differential — the code path
branches on `exists` (a `user.hash` on `None` crashes). It is a coarser
oracle (a crash, not a clean message) but it still reveals existence —
record `user-dependent 500` as the channel. A one-off `500` is a crash,
not a channel — re-send first.

## "The register needs an email — does the taken-check work on the username or the email?"

Often BOTH — `"username taken"` and `"email registered"` may be separate
checks. Probe the username field AND the email field independently; an
email-check enumerates emails (a different, often more valuable, list)
while a username-check enumerates usernames. Record which field leaks.

## "How do I enumerate when EVERY field is validated?"

Validation rejects a bad-FORMAT name (a `400`/`422`) — that is a format
error, not an oracle. Use a valid-format fake (`zzz-<valid-chars>`), and
the existence-oracle still fires on the valid-format pair. Validation
changes the NAME space, not the existence check.

## "The app returns a CAPTCHA on the second request — dead?"

No — the CAPTCHA's appearance is itself a signal (the app counts
attempts), and the content oracle may still fire within the pre-CAPTCHA
window. A CAPTCHA on register/reset but not check-username leaves the
direct oracle open. The CAPTCHA is a throttle measurement, not a
closure.

## "Can I enumerate a SAML/OIDC-federated app?"

Yes — a federated `user@external.com` gets a different
`SAMLRequest`/redirect than a local `user@local.com`, revealing which
directory holds the account. The federation leak is a redirect/`Location`
oracle on the SSO flow.

## "What if there's literally no differential anywhere?"

Then the app is genuinely hardened on the enum surface — record the
per-form, per-channel uniform measurements as a real negative, and the
chain moves to `web-auth-session`/`web-logic-flaw`/etc. A measured
"no oracle" is a complete outcome.
