# Negative results — what a dead end looks like

A negative result is a probe that produced no new signal — it is not a
falsifier (which closes a shape), and it is not a confirmation (which proves
one). Recording negatives is how the kill map is built.

## The negative shapes

| Probe | The negative | What it means |
|---|---|---|
| callback with mismatched state | `302 Location: /login` | the flow did not complete — the state was rejected, but no explicit mismatch was named |
| authorize with wrong redirect_uri | `400 Bad Request` (no detail) | the redirect_uri was rejected — but whether it was validated exactly or loosely is unclear |
| authorize with `response_type=token` | `400 Bad Request` | implicit flow is not accepted — but whether it is allowlisted or just not supported is unclear |
| authorize without `code_challenge` | `302` to consent page | PKCE is not required — but the code exchange may still re-validate |
| text/plain JSON login | `400 Bad Request` | the binder does not parse text/plain — the cookie-swap delivery is dead |
| replay a code | `400 invalid_grant` | the code is single-use or expired — the replay is dead |
| exchange with wrong `code_verifier` | `400 invalid_grant` | PKCE is enforced — the bypass is dead |
| exchange with different `client_id` | `400 invalid_client` | the code is bound to client_id — the cross-client shape is dead |

## The negative ledger

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict negative \
  --request "callback with mismatched state" \
  --result "302 Location: /login (no explicit mismatch named)"
```

## The negative-vs-falsifier distinction

| Observation | What it is | The next action |
|---|---|---|
| `400 Bad Request: state mismatch` | falsifier | the state-binding shape is dead — do not retry |
| `302 Location: /login` | negative | the flow did not complete — try a different probe (a different state, a different session) |
| `400 Bad Request` (no detail) | negative | the request was rejected — the shape may still be live with a different payload |
| `200 OK` with no session | negative | the flow completed but no session was established — the sink is not reached |

## The boundary record

A negative result should record the boundary it tested:

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict negative \
  --request "callback with mismatched state" \
  --result "302 Location: /login — state was rejected but no explicit mismatch named; boundary: state validation present, mechanism unclear"
```

The boundary record tells the next agent what was tested and what remains
untested — the mechanism is unclear, so a different state shape may still work.

## The kill map

When a shape is confirmed dead by a falsifier, the kill map records it. When
a shape produces a negative, the ledger records the boundary. The next agent
reads the kill map and the ledger, and does not re-walk dead ground.

```bash
# the falsifier record
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict falsifier \
  --request "callback with mismatched state" \
  --result "400 Bad Request: state mismatch — state is bound to session; the CSRF shape is dead"

# the negative record
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict negative \
  --request "callback with mismatched state" \
  --result "302 Location: /login — no explicit mismatch; mechanism unclear"
```
