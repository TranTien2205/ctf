# Integration notes — the CORS skill inside the controller loop

How the CORS depth skill plugs into the repository's control loop —
the classify → decide → probe → verdict → flag flow.

---

## 1. The entry — when the router names CORS

```text
the router or classify.py names 'web-cors' when:
- an ACAO/ACAC header appears in a response
- a 'cross-origin' or 'cors' signal is in the observation
- a bot/victim + a sensitive-API shape is present
→ the classify output is a CANDIDATE — not a finding.
```

```bash
python3 tools/classify.py "<the observation>"          # names the class
python3 tools/skill_select.py web-cors                  # opens this skill
```

## 2. The state — recording the challenge

```bash
python3 tools/state.py <name> --category web --target <url> \
  --challenge-name "<real name>" --event "<event>"
python3 tools/state.py <name> --source <dir>            # a white-box handout
```

## 3. The chain-match — has this shape been solved here

```bash
python3 tools/chain_match.py --source <dir> --record <name>
# a CORS card match → the card's probe; a family_lead → a READ, not a run
```

## 4. The hypothesis — the CORS probe as a ledger row

```bash
python3 tools/state.py <name> --hypothesis \
  "cors: ACAO=<v> ACAC=<t/f> on /api/<ep> — <shape> -> <exploit>"
```

## 5. The probe — the bounded measurement

```text
5 probes or 15 min per mechanism class; 25 or 45 for the challenge.
the CORS sweep: the measurement, the credential check, the battery,
the build, the delivery, the readback — each a bounded probe.
```

## 6. The verdict — through the write gate

```bash
# a confirms needs the exfil — the response bytes quoted
python3 tools/hooks.py post-probe <name> --verdict confirms \
  --hypothesis-id <H> --class web-cors --evidence-kind impact \
  --evidence 'read /api/<ep> cross-origin; flag exfiltrated' \
  --response '<the exfil hit bytes>'

# a refutes — a gate that held
python3 tools/hooks.py post-probe <name> --verdict refutes \
  --hypothesis-id <H> --class web-cors --evidence-kind class \
  --evidence 'ACAO fixed-allowlist — no bypass' --response '<the headers>'
```

## 7. The flag — through pre-flag

```bash
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source 'GET /x?d=<b64>' --evidence '<the exfil hit>'
# a flag-shaped string not in a live response → a CANDIDATE, not a flag
```

## 8. The escalation — when the CORS sweep is spent

```text
the budget exhausted → decide.py answers 'escalate':
- chain_match — a solved-shape match
- reclassify — a different bug class (JSONP/ws/postMessage/XS-leak)
- writeup_search — a known challenge
- novel_plan — a layered-handout plan
- fanout_sweep — a parallel multi-class sweep
- solver_handoff — a different solver
each rung recorded with state.py --strategy-used <rung>
```

## 9. The CORS-vs-reclassify — when it's not the class

```text
a `no-cors` write that fires → web-csrf — the request lands; CORS
doesn't gate it.
a script-tag serve            → JSONP/XSSI — a different read primitive.
a ws channel                  → web-websocket — a CSWSH read.
a page broadcast              → postMessage-hijack.
a side-channel measure        → web-xs-leaks.
→ reclassify is a legitimate escalation — record it.
```

## 10. The CORS-in-the-ledger — the solve's ancestry

```bash
# a solve files into the class's skill — the evidence chain intact
python3 tools/classify_solve.py --chain <id>
# a catalogue class's first solve promotes it to verified — the card
# is written to knowledge/chains/<id>.json
```

## 11. The decide-loop — the controller's answers

```text
run_probe    → the next bounded CORS probe — the measurement
switch_class → a different bug class — a JSONP/ws/postMessage pivot
novel_plan   → a layered-handout plan — a multi-step CORS chain
verify_flag  → the flag gate — the pre-flag check
record_solve → the solve filed — the chain card written
escalate     → a spent budget's strategy — the named rung
stop_report  → every rung spent — the kill map to knowledge/attempts/
```

## 12. The CORS-solve integration — the full loop

```text
classify → 'web-cors' → this skill → the measurement → the exploit
→ the exfil → the flag → the chain card → the class promoted
```
