# Per-check CSRF — the state-binding check, with the full mechanics

The per-check-csrf module names the `state`-binding check. This module
carries the full mechanics — the probe, the confirmation, the falsifier,
and the escalation.

## The check

`state` is the CSRF binding — the random value that binds the authorize
request to the callback. When it is bound to the session, a flow started by
one party cannot be completed by another. When it is not bound, the callback
accepts a `state` that was issued for a different session.

## The probe

```bash
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=DIFFERENT"
```

The `state` is `DIFFERENT` — a `state` the session never stored. The
callback's response is the check.

## The confirmation

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=victim_session; HttpOnly; Path=/
```

A `302` + `Set-Cookie: session=...` — the session is issued on the victim's
account. The `state` is not bound to the session — the CSRF shape is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "state mismatch"}
```

A `400` naming the mismatch — the `state` is bound to the session. The CSRF
shape is dead.

## The escalation

Login-CSRF or linking-CSRF — the victim visits the attacker's authorize URL;
the IdP issues a code for the victim's account; the callback accepts the
`state` and issues a session on the victim's account.

## The evidence rules

- A `302` + `Set-Cookie: session=...` is the session confirmation.
- A `400` naming the mismatch is the falsifier.
- A `302` to a login page is a negative, not a falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `state` bound to session | `400 state mismatch` | dead |
| `state` bound to code | `callback?code=STOLEN_CODE&state=STOLEN_STATE` accepted | live on the code-binding surface |
| `state` not bound | `302` + `Set-Cookie: session=...` | live |
| `state` single-use | `400` on replay | dead |
| `state` predictable | `state=12345` | live |
