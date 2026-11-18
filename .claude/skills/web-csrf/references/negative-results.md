# Negative results — recording the gates that held

A `refutes` verdict is as valuable as a `confirms` — it closes a
gate, names the class boundary, and prevents re-walking dead paths.
The kill-map of CSRF negatives.

---

## 1. Why negatives matter

```text
CSRF fails by GATE, not by absence — each gate that holds is a
named falsifier that:
- closes this endpoint for this class
- routes to the class that bypasses it (XSS for a stored context,
  CORS-open for a read, SSRF for a server-fetch)
- prevents a retry that wastes a bot cycle
```

## 2. The falsifier ledger

```bash
# each gate that held → a refutes verdict
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-csrf --evidence-kind class \
  --evidence 'the gate that held' --response '<the refusal body>'

# and a state note for the kill-map
python3 tools/state.py <c> --hypothesis "refutes: <gate>"
```

## 3. The gate-specific refutes templates

```text
refutes: SameSite=Strict on the only credential — no cross-site attach
refutes: SameSite=Lax + the write is POST-only — no GET-write exists
refutes: token required AND session-bound — replay under another
         session failed
refutes: token required AND unreadable cross-origin — no leak surface
refutes: Origin enforced exactly — foreign/substring/null all rejected
refutes: Referer enforced + can't be stripped to bypass
refutes: content-type whitelisted to application/json — text/plain 415
refutes: the write is inert — lands but does nothing useful
refutes: no viewer/delivery vehicle — no bot, no stored context
refutes: the bot can't reach the write's host (airgapped loopback)
refutes: ws-hijack blocked — Origin checked on handshake
refutes: Partitioned cookie — third-party attach dead
```

## 4. The "which gate refused" attribution

```text
a CSRF failure is ONLY useful if you name WHICH gate held:
- 'the write didn't land' is uninformative
- 'the cookie didn't attach — SameSite=Strict' is a falsifier
- 'the token rejected the request' is a falsifier
- 'the content-type was rejected — 415' is a falsifier
```

The attribution decides the pivot — a Strict cookie routes to a
different credential; a token routes to a token-bypass or XSS; a
content-type routes to a sibling route.

## 5. The inconclusive negatives — couldn't decide

```text
- the bot visited but no state change AND no clear gate refusal →
  inconclusive — could be a slow oracle, a partial write, a missed
  field
- the delivery fired but the readback is ambiguous → inconclusive
an inconclusive isn't a refutes — it's an unknown that needs a
different oracle or a longer window.
```

## 6. The kill-map entry — what's closed

```text
knowledge/attempts/<challenge>.json records the dead layers:
- 'web-csrf on /update_tornado: remote_ip gate is socket-peer — the
  ONLY local client is the bot; the form-nav shape is the open path'
- 'web-csrf on /change: token session-bound — closed for direct;
  a stored-content page is the remaining vector'
each entry names the precondition that would reopen the layer.
```

## 7. The pivot — the class that bypasses the held gate

| Gate that held | The pivot |
|---|---|
| SameSite=Strict | a stored-content page (same-origin) or a non-cookie credential |
| token session-bound | an XSS that reads the token, or a token-bypass shape |
| Origin/Referer enforced | a stored page, or a subdomain-trust bypass |
| json-only content-type | a sibling urlencoded route, or a server-fetch (SSRF) |
| no delivery vehicle | a stored page's viewer, or a social hook — or a different class entirely |
| Partitioned cookie | a first-party (same-site) context |

## 8. The budget-discipline on negatives

```text
5 probes or 15 min per gate-family — when the gate is measured closed,
stop testing that gate's variants. a 'the token might be bypassable'
hope that burns 5 probes on token-strips is the Polynomial lesson —
name the falsifier and move to a different gate or class.
```

## 9. The negative→positive — when a refutes opens a path

```text
a refutes that names 'SameSite=Strict on cookie-A' can coexist with
a candidate on 'cookie-B is missing SameSite' — a different credential
channel. each refutes is scoped to ITS credential/endpoint — a
different credential or a different endpoint is a new measurement,
not a retry.
```

## 10. The final falsifier — the whole class closed

```text
when EVERY gate holds AND no stored-content/sibling/non-cookie
vector exists:
  the endpoint is not CSRF-able — record the full refutes and pivot
  to the class that reaches the write differently (XSS for a stored
  context, an access-control bug on the write itself, SSRF for a
  server-fetch). a fully-falsified CSRF is a clean result.
```
