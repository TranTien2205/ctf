# Negative results — what to record when the answer is no

A negative is a measurement with a falsifier attached. Recording it stops
the next pass (or the next agent) from re-proving it.

## Format

For each dead layer: what was tried, what was observed (verbatim where
possible), and the precondition that would reopen it.

## The standard negatives

| Tested | Negative observation | Reopens if |
|---|---|---|
| ECB | no duplicate block in 'A'*48 | a different injection point exists |
| Padding oracle | identical reject for every corruption | a second endpoint decrypts |
| Nonce reuse | all captured nonces distinct | more captures become available |
| Length extension | forge rejected at secret-len 8..64 | construction shown to be raw-hash |
| Bit-flip | parser rejects all garbage blocks | a don't-care field is found |
| Timing oracle | distributions overlap at 200 samples | the service gets quieter |
| Key path | no key/seed material in handout | new source surfaces |

## Recording

Field notes: `../field-notes.md` — one line per dead layer, with the probe
that produced it. If the whole class closed (authenticated boundary),
record that as the final entry and hand back to the router.

## Anti-pattern

A negative without the probe is not a negative — 'padding oracle didn't
work' records nothing. 'pad-corrupt and MAC-corrupt both returned identical
403 on 12 corruptions' records a closed layer.
