# Operator-Guided CTF Loop

This is a suggested manual workflow, not an implemented autonomous loop.
The planner emits suggestions; operators execute probes and update state.
Retry limits, confidence updates, and flag verification are not automated.

Use this for a private or unknown challenge where no reliable writeup exists.

```text
observation -> attack surface -> hypotheses -> cheapest discriminating probe
-> result vs baseline -> confidence update -> next probe -> flag verification
```

Rules:

- Keep at most three open hypotheses.
- Every hypothesis must cite an observation and have a falsifier.
- Prefer a probe that distinguishes two hypotheses over a payload that merely
  attempts exploitation.
- After three probes without new signal, close the hypothesis and switch class.
- Do not load depth references before the first useful probe unless the input
  format itself is unknown.
- A timeout is evidence about availability/processing, not proof of a bug.
- A flag-shaped string is a candidate until read from the target/artifact.

Required iteration:

```text
HYPOTHESIS: class + reason
FALSIFIER: observation that would close it
PROBE: one reversible action
EXPECTED: distinguishing signal
RESULT: observed response
UPDATE: confidence up/down/closed
NEXT: one action
```
