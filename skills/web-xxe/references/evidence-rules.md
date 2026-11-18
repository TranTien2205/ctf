# Evidence Rules — what counts, what doesn't

## The confirm standard — `hooks.py post-probe --verdict confirms`

- `--evidence` = a VERBATIM substring of `--response` — the gate checks
  substring containment
- `--response` = the actual bytes the request returned, not a paraphrase
- `--evidence-kind class` for "entities expand" vs `--evidence-kind
  impact` for "I read /etc/passwd"

## What confirms the CLASS (XXE is live)

- internal `&probe;` echoes back `XXE_PROBE` where the literal `&probe;`
  was sent — evidence = the echo line containing `XXE_PROBE`
- external `file:///etc/passwd` returns `root:x:0:0:...` lines —
  evidence = the verbatim passwd line
- an external-DTD fetch hits your `oob_listener` log — evidence = the
  verbatim hit line `GET /e.dtd`
- a parser error naming the entity/`SYSTEM` URI — evidence = the
  exception text carrying your URI

## What does NOT confirm

- the parser error alone — `SAXParseException` just proves an XML parser
  exists, not that entities resolve — falsifier-grade, not confirm-grade
- a timeout or 500 on an external entity — could be egress-blocked, not
  necessarily resolution — inconclusive
- a flag-shaped string in the response that wasn't put there by entity
  substitution — a template echo, a reflection of your own input —
  `&probe;` echoed as literal `&probe;` is NOT evidence (it's a
  no-expansion negative)

## The OOB-hit evidence standard

A hit on your listener is only YOURS if the URL carries your canary —
`oob_listener.py canary` generates it. A bare hit on port 8000 could be
the target's health-check or another player on shared infra.

## The flag standard — `hooks.py pre-flag`

- the flag must appear inside the entity-substituted content in the
  response OR inside an OOB-captured URL — verbatim
- `python3 tools/hooks.py <name> pre-flag --value "<flag{...}>" --source
  "<where it came from>"` — the gate decides

## The negative record — count what died

A killed falsifier is a result. Record `verdict=refutes` with the
evidence the response gave — `DOCTYPE rejected`, `EntitiesForbidden`,
`DtdProcessing` errors — they close the class cleanly for the ledger.

## The two-channel separation

An XXE finding is often TWO evidence records: the in-band echo (class)
and the OOB hit (exfil channel). Record both separately — each gets its
own `post-probe`.
