# Common mistakes deep — the OAuth traps with the full mechanics

The common-mistakes module names the traps. This module carries the full
mechanics — why each trap happens, what the evidence actually shows, and
how to avoid it.

## Mistake 1 — testing `state` before the transcript exists

The `state` binding is tested by replaying a callback — but the callback is
only meaningful in the context of the session that started the flow. Testing
`state` without first capturing which session stored which `state` makes the
test unattributable.

**Why it happens**: the agent sees a `state` parameter in the URL and tests
it immediately, without recording which session it was issued for.

**What the evidence actually shows**: a `state` that is not bound to *this*
session may still be bound to *a* session — the callback rejects a random
`state` not because `state` is not bound, but because it was never stored.

**The fix**: walk the whole flow once with a named jar, record which session
stored which `state`, then replay a `state` from a *different* session.

## Mistake 2 — confusing `state` not validated with `state` not bound

`state` not validated at all is a different bug from `state` not bound to
the session. The first means any `state` is accepted; the second means a
`state` from one session is accepted by another.

**Why it happens**: both produce a `302` to the app on a mismatched `state` —
the agent assumes the mechanism is the same.

**What the evidence actually shows**: a `state` that is not validated at all
accepts a `state` the app never issued. A `state` that is not bound to the
session accepts a `state` that was issued for a *different* session.

**The fix**: test both — a `state` the app never issued (random), and a
`state` from a different session (cross-session). Each names a different
mechanism.

## Mistake 3 — assuming `redirect_uri` loose means code delivery

A loose `redirect_uri` validation delivers the code to an attacker-controlled
endpoint — but the code exchange still requires `client_id` + `client_secret`
+ the same `redirect_uri`. If the `client_secret` is not known, the code is
useless for a direct exchange — it can only be replayed against the app's
own callback.

**Why it happens**: the agent sees the code delivered to `evil.com` and
assumes the exchange is possible.

**What the evidence actually shows**: the code is bound to `redirect_uri` on
exchange — a code minted for `https://app/callback` cannot be exchanged with
`redirect_uri=https://evil.com/callback`. The interception only works as a
replay against the app's own callback, which carries the same `redirect_uri`.

**The fix**: check whether the `redirect_uri` on the token request must match
the authorize step's exactly. If it must, the interception only works as a
replay — the attacker replays the stolen code against `https://app/callback`,
not `https://evil.com/callback`.

## Mistake 4 — treating the cookie swap as a session bug

The cookie swap is not a session bug — it is a delegation bug. The app's
session is fine; the IdP's token cookie was overwritten. The app delegates
identity to the IdP's token, so the session follows the token.

**Why it happens**: the agent sees a session established on the attacker's
account and assumes the session was hijacked.

**What the evidence actually shows**: the app's session cookie is unchanged —
the IdP's token cookie was overwritten. The session follows the token because
the app delegates identity to it.

**The fix**: record which cookie was swapped (the IdP token), not which
session was established (the app's). The evidence is the `Set-Cookie` that
overwrote the IdP token, not the session ID.

## Mistake 5 — assuming implicit flow means the token is always leaked

Implicit flow puts the token in the fragment — but the fragment only leaks
when the callback page loads a subresource that carries it in `Referer`, or
when the token is stored in `localStorage`/`sessionStorage` and read by a
same-origin script, or when the history is re-navigated.

**Why it happens**: the agent sees `response_type=token` and assumes the
token leaks.

**What the evidence actually shows**: the fragment is in the URL but not in
the request — the server does not see it. The leak requires a subresource
request that carries the fragment in `Referer`, or a script that reads
`window.location.hash`.

**The fix**: check what the callback page actually loads — a tracking pixel,
an analytics beacon, a CDN script — before claiming the leak. A `Referrer-Policy`
header that strips the fragment closes the Referer leak.

## Mistake 6 — confusing PKCE not required with PKCE bypass

PKCE not required means a flow without `code_challenge` is accepted. PKCE
bypass means a code minted with `code_challenge` is exchangeable without
`code_verifier`. Both matter, but they are different bugs.

**Why it happens**: both allow a stolen code to be exchanged — the agent
assumes the mechanism is the same.

**What the evidence actually shows**: PKCE not required means the code was
never bound to a verifier — anyone can exchange it. PKCE bypass means the
code was bound to a verifier, but the verifier is not re-validated — the
exchange succeeds with a wrong verifier.

**The fix**: test both — a flow without `code_challenge` (is PKCE required?),
and a code minted with `code_challenge` exchanged with a wrong `code_verifier`
(is the verifier re-validated?).

## Mistake 7 — treating the registration race as a race-condition bug

The registration race is a race-condition primitive — but the *class* is
OAuth/SSO because the race is the delivery mechanism for the cookie swap.
The race wins the account; the swap hijacks the session; the `loginSSO`
parameter confusion lands the flag.

**Why it happens**: the agent sees a race and classifies it as
`web-race-condition`.

**What the evidence actually shows**: the race is the delivery — the class
is the OAuth/SSO surface because the impact is a session hijack via the
cookie swap.

**The fix**: record the class as `web-oauth-sso`, the mechanism as a
registration race, and the chain as race → swap → parameter confusion →
flag submit.

## Mistake 8 — assuming `sub` is always safe

`sub` is the IdP's stable subject identifier — not attacker-controlled. But
some IdPs let the user choose their `sub` (a self-registered username), or
the `sub` is derived from a user-controlled field. Check whether `sub` is
truly immutable.

**Why it happens**: the agent assumes `sub` is the IdP's assigned identifier.

**What the evidence actually shows**: a `sub` that is a self-registered
username is attacker-controlled — the pre-registration race wins on `sub`
as well as on `email`.

**The fix**: read the IdP's registration flow — does the user choose the
`sub`, or is it assigned? A `sub` that is a `preferred_username` or a
user-chosen field is not safe.

## Mistake 9 — testing the falsifier as a negative

A falsifier is an observation that closes the shape — it is not a negative
result to be retried. Retrying a falsifier wastes budget on a dead shape.

**Why it happens**: the agent sees a `400` and treats it as a negative — a
probe that did not produce a signal — rather than a falsifier that closes
the shape.

**What the evidence actually shows**: a `400` naming the mismatch is a
falsifier — the shape is dead. A `302` to a login page is a negative — the
flow did not complete, but the shape may still be live with a different
probe.

**The fix**: record the falsifier explicitly — `400 Bad Request: state
mismatch` closes the state-binding shape; do not retry it. Record the
negative separately — `302 Location: /login` means the flow did not complete;
a different probe may still work.

## Mistake 10 — confusing the code leak with the code exchange

A code in the URL is a code that leaks — via `Referer`, via history, via
logs. But the leak is only useful if the code is exchangeable — which
requires the `client_secret` and the same `redirect_uri`. A leaked code
without the secret is only useful as a replay against the app's callback.

**Why it happens**: the agent sees a code in the URL and assumes it can be
exchanged.

**What the evidence actually shows**: the code is bound to `redirect_uri` on
exchange — a code minted for `https://app/callback` cannot be exchanged with
`redirect_uri=https://evil.com/callback`. The leak is only useful as a
replay — the attacker replays the stolen code against `https://app/callback`,
which requires the `state` to also be unbound.

**The fix**: distinguish the leak surface (the code in the URL) from the
exchange surface (the token request's re-validation). The leak buys a code;
the exchange buys a token. They are different bugs.
