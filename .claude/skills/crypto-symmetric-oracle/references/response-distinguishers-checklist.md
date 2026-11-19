# Response distinguishers — what counts as an oracle signal — operational checklist

A padding oracle needs TWO distinguishable answers. Enumerate the channels: status, body text, length, timing, connection behavior. Document the distinguisher BEFORE running the loop.

## Checklist

- [ ] Baseline: capture the response for a VALID ciphertext.
- [ ] Corrupt the pad-producing byte; diff every channel against baseline.
- [ ] Corrupt a byte that keeps padding valid but breaks MAC/decode; diff again — need distinct answers for the two corruptions.
- [ ] Pick the channel with the clearest split and feed it to --ok-status/--ok-regex.
- [ ] Validate the distinguisher on 5+ random corruptions before trusting the loop.

## Abort conditions

- Error text that LOOKS different but comes from the HTTP framework (not the crypto layer) is still a valid distinguisher — use it.
- Timing-only oracles are fragile: warmup, jitter, and averaging are mandatory; 5 samples is not a measurement.
- A catch-all error page with identical body but different CONTENT-LENGTH is still distinguishable.

## Falsifier

Falsifier — every corruption produces an identical answer across all channels, including averaged timing: no oracle exists.

## Cross-references

`cbc-padding-oracle.md` · `tools-pad-oracle.md`
