# Response distinguishers — what counts as an oracle signal

A padding oracle needs TWO distinguishable answers. Enumerate the channels: status, body text, length, timing, connection behavior. Document the distinguisher BEFORE running the loop.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Status 200 vs 500/403 | direct oracle | pad_oracle --ok-status/--ok-regex |
| Same status, different body | body oracle | --ok-regex on the difference |
| Same status and body, different length | length oracle | still distinguishes |
| Identical responses, timing split >20ms | timing oracle | requires averaged samples |
| All channels identical | no oracle | class closed |

## Steps

1. Baseline: capture the response for a VALID ciphertext.
2. Corrupt the pad-producing byte; diff every channel against baseline.
3. Corrupt a byte that keeps padding valid but breaks MAC/decode; diff again — need distinct answers for the two corruptions.
4. Pick the channel with the clearest split and feed it to --ok-status/--ok-regex.
5. Validate the distinguisher on 5+ random corruptions before trusting the loop.

## Falsifier

Falsifier — every corruption produces an identical answer across all channels, including averaged timing: no oracle exists.

## Traps

- Error text that LOOKS different but comes from the HTTP framework (not the crypto layer) is still a valid distinguisher — use it.
- Timing-only oracles are fragile: warmup, jitter, and averaging are mandatory; 5 samples is not a measurement.
- A catch-all error page with identical body but different CONTENT-LENGTH is still distinguishable.

## Commands

```bash
python3 tools/pad_oracle.py --ct <h> --url 'https://t/d?c={CT}' --ok-regex 'OK'
```

## Cross-references

`cbc-padding-oracle.md` · `tools-pad-oracle.md`
