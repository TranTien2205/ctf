# Verified chains — the honest state of the class

## The honest statement

`web-websocket` is a **catalogue** class — no `knowledge/chains/` card
records a local solve of a WebSocket challenge. The corpus is standard
published guidance, not local experience. Never present it as a solved
class; never claim a technique here worked.

## What a verified chain card would look like

```
id:          web-websocket-<challenge-name>
class:       web-websocket (cswsh|unauth|idor|dispatch|spoof|inject)
challenge:   <the challenge + the event>
signals:     [the observable literals that matched]
probe:       <the verbatim first_confirming_probe>
falsifier:   <the uniform-rejection that would kill it>
chain[]:     [the verbatim steps + replies]
blast_radius: <shared-instance caution>
flag_route:  <the flag-closing class>
```

## The promotion path

A local solve promotes the class — a chain card records the verbatim
chain; `tools/classify_solve.py --chain <id>` files it; the class's
evidence level rises from `catalogue` to `verified`. The card carries
the local traps — the real `SameSite` gotcha, the real framing — that
the generic corpus cannot name.

## The catalogue-honest boundary

- a confirmed local chain → verified, on the card
- a standard published technique → catalogue, this corpus
- a writeup's claim → untrusted data, not local proof

## The verified-chain search

```bash
python3 tools/chain_match.py --source <dir> --record <name>
# or the black-box observation
python3 tools/chain_match.py "<the ws observations>" --record <name>
```

A `strong` match → the card's own probe; a `family_leads`/`weak` match
→ a card to READ, never a probe to run.

## The record discipline

A confirmed web-websocket chain is the FIRST verification — record it
verbatim + file it; the corpus does not pretend the class was already
solved.
