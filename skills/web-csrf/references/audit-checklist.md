# Audit checklist — the pre-flight and the post-landing checks

The pre-delivery checklist that catches the common failures, and
the post-landing verification that proves the write.

---

## Pre-delivery — the gate checklist

```text
□ the write exists — a state-changing endpoint, not a read-only GET
□ the viewer exists — a bot/victim/stored-context to deliver through
□ the credential named — a cookie (which?), a position, a jar
□ the cookie's SameSite read — Strict/Lax/None/missing/Partitioned
□ the token checked — strip it, replay it, is it session-bound?
□ Origin/Referer measured — foreign, absent, null, substring all tried
□ the content-type a form can produce — or a lenient-parse accepts
□ the write's bind model — does it drop extra keys? require fields?
□ the delivery context reachable — external/data:/stored/subdomain?
□ the mixed-content/PNA constraint — a form nav for loopback, http
  for http-target
```

## The delivery checklist — before the bot cycle

```text
□ the page self-contains everything (no external JS the sandbox blocks)
□ the submit() is the FIRST script line (a bot closing fast still fires)
□ a form nav for a loopback target (not fetch — PNA)
□ an http or data: page for an http target (not https — mixed content)
□ a marker on the write — a unique attributed value
□ an OOB beacon if the page can reach you — the load-confirmation
□ one URL per bot cycle — the page carries the whole write
```

## The readback checklist — proving the write

```text
□ the oracle named — which readback proves the state change
□ the marker read — a unique value only your payload produces
□ the before/after — a delta measured, not just 'something changed'
□ the attribution — the state change is YOUR write, not another's
□ the flag's home — where the flag lands if the write extracts it
```

## The verdict checklist — the recording

```bash
# candidate — a gate opened
python3 tools/state.py <c> --hypothesis "candidate: <gate> open"

# confirms — the write landed + readback
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-csrf --evidence-kind impact \
  --evidence '<the marker/delta>' --response '<the response bytes>'

# refutes — a gate held
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-csrf --evidence-kind class \
  --evidence '<the gate that held>' --response '<the refusal>'

# flag — read from a live response
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source 'GET /api/me' --evidence '<the response>'
```

## The stop conditions — when to halt

```text
□ the same delivery tried 3 times with no new signal → change it
□ a class falsifier observed (unreadable token, Strict+no vector,
  enforced Origin, json-only+strict) → record refutes, pivot
□ the per-mechanism budget spent (5 probes / 15 min) → a different
  gate or a different class
□ the whole-challenge ceiling (25/45) → escalate via decide.py
```

## The chain_match first — always

```bash
python3 tools/chain_match.py --source <dir> --record <name>
# before inventing — the TornadoService/SSOS cards carry the shapes
```
