# Class boundary

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

This class answers 'the browser sent a state-changing request the
user did not intend, because the app could not tell it from an intended
one'. It does not answer: whether the injected content executes (XSS),
whether a token can be read cross-origin (CORS), whether two requests
arrive in a bad order (race-condition), or whether the action was
authorized for THIS user (idor). Each sibling names its own evidence:
CSRF's is the missing/weak defence plus an accepted forged request.

## The one-sentence test

Same request with cookies = accepted; same request without cookies =
refused; the ONLY difference is ambient authority -> the app trusted
the cookie's presence, not the request's intent.

## Pivot

Boundary applies -> route to the sibling, do not stretch the claim.
