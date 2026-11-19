# Response distinguishers — what counts as an oracle signal — case catalogue

A padding oracle needs TWO distinguishable answers. Enumerate the channels: status, body text, length, timing, connection behavior. Document the distinguisher BEFORE running the loop.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Status 200 vs 500/403 | direct oracle | pad_oracle --ok-status/--ok-regex |
| 2 | Same status, different body | body oracle | --ok-regex on the difference |
| 3 | Same status and body, different length | length oracle | still distinguishes |
| 4 | Identical responses, timing split >20ms | timing oracle | requires averaged samples |
| 5 | All channels identical | no oracle | class closed |

## Falsifier

Falsifier — every corruption produces an identical answer across all channels, including averaged timing: no oracle exists.

## Coverage notes

- Error text that LOOKS different but comes from the HTTP framework (not the crypto layer) is still a valid distinguisher — use it.
- Timing-only oracles are fragile: warmup, jitter, and averaging are mandatory; 5 samples is not a measurement.
- A catch-all error page with identical body but different CONTENT-LENGTH is still distinguishable.

## Cross-references

`cbc-padding-oracle.md` · `tools-pad-oracle.md`
