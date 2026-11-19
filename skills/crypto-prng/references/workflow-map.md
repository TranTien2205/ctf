# Workflow map — phase → procedure → files

## The map

```
read      → detection*.md                    → parse + fingerprint
gate      → per-check*/per-boundary*         → count + raw + window
route     → cipher-identification/matrix     → pick attack
solve     → payload-dictionary*/per-attack-* → crypto_attack.py
verify    → verify*/per-check*               → predict == held
record    → field-notes*/evidence*           → post-probe
escalate  → falsifiers*/negative/decide.py   → rung
```

## Phase → files

| Phase | Files |
|---|---|
| read | `detection*.md`,`recon-order*.md`,`probe-order*.md` |
| gate | `per-check*.md`,`per-boundary*.md`,`detection-checklist*.md` |
| route | `per-family-*.md`,`per-attack-*.md`,`cipher-identification.md` |
| solve | `payload-dictionary*.md`,`workflow*.md`,`*-deep.md` |
| verify | `verify*.md`,`per-check*.md` |
| record | `field-notes-*.md`,`evidence*.md`,`verified-chains*.md` |
| escalate | `falsifiers*.md`,`negative-results*.md`,`decide.py` |

## The support files

- `operator-notes*.md` — helpers (outputs, normalize, fingerprint).
- `troubleshoot*.md` — fixes.
- `common-mistakes*.md`,`anti-patterns*.md` — traps.
- `evasion*.md`,`edge-cases*.md` — disguises.
- `case-studies*.md`,`worked-examples*.md` — narrated solves.
