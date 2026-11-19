# Summary (deep) — the complete one-file orientation

## The class in one paragraph

```text
A request value (a redirect param) lands in a Location:/meta/JS carrier;
the server emits an attacker-controlled DESTINATION the client navigates
to cross-origin. Alone it's a phishing launder; the class's value is the
downstream trust it feeds — the OAuth code, the SSRF fetch, the XSS, the
bot visit. The confirm is a verbatim Location: carrying the canary; the
falsifier is a safe Location on every canary + bypass arm.
```

## The mechanism in one diagram

```text
param -> filter -> resolution -> carrier -> navigation -> launder
  |        |          |           |           |             |
  |        |          |           |           |             + the chain value
  |        |          |           |           + the WHATWG parse
  |        |          |           + Location/meta/JS/Refresh
  |        |          + verbatim/decode/join/template
  |        + the check's parse — the bypass lives here
  + next/url/redirect_uri/...
```

## The first-probe in one line

```bash
curl -si "$BASE/login?next=https%3A%2F%2Fattacker.invalid" | grep -i '^location'
```

## The corpus in one table

| The layer | The files |
|---|---|
| the model | mechanism* theory class-boundary glossary summary |
| the detection | detection* param-inventory per-param per-endpoint per-surface |
| the bypass corpus | filter-bypass* per-check per-vector per-boundary per-target payload-* encoding-attacks evasion extended-corpus boundary-map |
| the parser gaps | parser-differentials framework-matrix |
| the carriers | client-side stored-and-referer per-channel per-mechanism edge-cases |
| the chains | chain-routes per-route multi-step-chains attack-shapes exploitation second-order |
| the evidence | evidence-rules* detection-verdicts |
| the falsifiers | falsifiers* per-falsifier |
| the negatives | negative-* |
| the workflow | workflow* field-manual first-hour recon-order detection-workflow detection-playbook |
| the checklists | checklist* detection-checklist |
| the reference | quick-reference* decision-* lead-grammar probe-* per-*-map mechanism-index detection-index* detection-map detection-surface |
| the discipline | common-* anti-patterns troubleshoot* edge-cases |
| the cases | case-studies real-world-cases |
| the state | verified-chains field-notes-deep preconditions* |

## The verdict in one table

| The observation | The verdict |
|---|---|
| `Location: <canary>` verbatim | `confirms` — `evidence-kind class` |
| `Location: <safe>` on one arm | `negative` — that arm blocked |
| `Location: <safe>` on ALL arms | `falsifies` — the class closed |
| no `Location` on a guessed param | `negative` (weak) — wrong param |
| a meta/JS carries the canary | `confirms` — the client-side twin |
| the chain's downstream fires | `confirms` — `evidence-kind impact` |

## The discipline in one list

- the verbatim `Location:` is the evidence — never "it redirected"
- `curl -si` + `grep -i location` — never `-L`
- one param, one arm at a time — an attributable `Location:`
- the fingerprint names the arms — don't blind-sweep
- a uniform `Location: <safe>` closes the surface — the arms-tried is the evidence
- a confirmed canary routes to `chain-routes.md` — the laundered-trust
- the class is CATALOGUE — the verbatim `Location:`-canary is the local confirm

## The contract in one line

```text
send one external destination; read the verbatim Location; a canary in
the Location confirms; a safe Location on every arm is the falsifier;
route the confirm to the laundered-trust chain for the flag-path
```
