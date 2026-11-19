# Common mistakes — the OAuth traps that cost time

The OAuth flow is a sequence of redirects and cookie writes. The mistakes are
usually about which step's trust is being tested, or about what the evidence
actually shows.

## Mistake 1 — testing `state` before the transcript exists

The `state` binding is tested by replaying a callback — but the callback is
only meaningful in the context of the session that started the flow. Testing
`state` without first capturing which session the state was stored in makes
the test unattributable.

**Fix**: walk the whole flow once with a named jar, record which session
stored which `state`, then replay.

## Mistake 2 — confusing `state` not validated with `state` not bound

`state` not validated at all is a different bug from `state` not bound to
the session. The first means any `state` is accepted; the second means a
`state` from one session is accepted by another.

**Fix**: test both — a `state` the app never issued, and a `state` from a
different session. Each names a different mechanism.

## Mistake 3 — assuming `redirect_uri` loose means code delivery

A loose `redirect_uri` validation delivers the code to an attacker-controlled
endpoint — but the code exchange still requires `client_id` + `client_secret`
+ the same `redirect_uri`. If the `client_secret` is not known, the code is
useless for a direct exchange — it can only be replayed against the app's
own callback.

**Fix**: check whether the `redirect_uri` on the token request must match the
authorize step's exactly. If it must, the interception only works as a replay.

## Mistake 4 — treating the cookie swap as a session bug

The cookie swap is not a session bug — it is a delegation bug. The app's
session is fine; the IdP's token cookie was overwritten. The app delegates
identity to the IdP's token, so the session follows the token.

**Fix**: record which cookie was swapped (the IdP token), not which session
was established (the app's).

## Mistake 5 — assuming implicit flow means the token is always leaked

Implicit flow puts the token in the fragment — but the fragment only leaks
when the callback page loads a subresource that carries it in `Referer`, or
when the token is stored in `localStorage`/`sessionStorage` and read by a
same-origin script, or when the history is re-navigated.

**Fix**: check what the callback page actually loads — a tracking pixel, an
analytics beacon, a CDN script — before claiming the leak.

## Mistake 6 — confusing PKCE not required with PKCE bypass

PKCE not required means a flow without `code_challenge` is accepted. PKCE
bypass means a code minted with `code_challenge` is exchangeable without
`code_verifier`. Both matter, but they are different bugs.

**Fix**: test both — a flow without `code_challenge`, and a code minted
with `code_challenge` exchanged with a wrong `code_verifier`.

## Mistake 7 — treating the registration race as a race-condition bug

The registration race is a race-condition primitive — but the *class* is
OAuth/SSO because the race is the delivery mechanism for the cookie swap.
The race wins the account; the swap hijacks the session; the `loginSSO`
parameter confusion lands the flag.

**Fix**: record the class as `web-oauth-sso`, the mechanism as a registration
race, and the chain as race → swap → parameter confusion → flag submit.

## Mistake 8 — assuming `sub` is always safe

`sub` is the IdP's stable subject identifier — not attacker-controlled. But
some IdPs let the user choose their `sub` (a self-registered username), or
the `sub` is derived from a user-controlled field. Check whether `sub` is
truly immutable.

**Fix**: read the IdP's registration flow — does the user choose the `sub`,
or is it assigned?

## Mistake 9 — testing the falsifier as a negative

A falsifier is an observation that closes the shape — it is not a negative
result to be retried. Retrying a falsifier wastes budget on a dead shape.

**Fix**: record the falsifier explicitly — `400 Bad Request: state mismatch`
closes the state-binding shape; do not retry it.

## Mistake 10 — confusing the code leak with the code exchange

A code in the URL is a code that leaks — via `Referer`, via history, via
logs. But the leak is only useful if the code is exchangeable — which requires
the `client_secret` and the same `redirect_uri`. A leaked code without the
secret is only useful as a replay against the app's callback.

**Fix**: distinguish the leak surface (the code in the URL) from the exchange
surface (the token request's re-validation).
