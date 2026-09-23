# Agent-assisted CTF verification

Use this reference when an agent, script, or solver brain proposes a flag or
claims that a challenge is solved.

## Trust boundaries

Treat agent-generated files as claims, not proof. In particular, an agent that
writes both `flag.txt` and `repro.sh` controls both the claimed value and the
purported reproduction. A reproduction that only prints the candidate does not
prove that the target or supplied artifact produced it.

Prefer an independent verifier, in this order:

1. A flag hash supplied by the lab manifest, checked before the flag enters
   state.
2. The challenge's supplied `flagCheck` or equivalent canonical checker.
3. A fresh live response or a supplied artifact excerpt that contains the
   candidate, captured verbatim and passed through the normal evidence hook.

If no independent verifier exists, keep the value as a candidate and label the
uncertainty. Do not promote it because a model is confident or because its own
script exits successfully.

## Evidence labels

- `live-response`: the value was read from the authorized live target response.
- `artifact`: the value was read from supplied source, a dump, or a locally
  reproduced instance. A local reproduction is not a live target response.
- `candidate`: a proposed value without an accepted proof excerpt; it must not
  enter solved state.

Use the narrowest truthful label. A source-only challenge can be solved from an
artifact, but must not be reported as a remote live-response solve.

## Rejection and retry

When an independent verifier rejects a candidate:

1. Preserve the rejected value and raw output for debugging.
2. Do not call the flag hook for that value.
3. Re-read the source, checker, hints, and exact application logic.
4. Try a new candidate; do not generate syntax variants of the rejected value.
5. Stop after the controller's retry/time budget and report unresolved status.

For a solver brain, a bounded `reject -> feedback -> retry` loop is useful. The
loop must be bounded and the verifier must remain independent of the agent.

## Launcher hygiene

Wrapper scripts must not overwrite process-wide variables such as `HOME`,
`PATH`, or `XDG_CONFIG_HOME` when they only need a repository root. Use a
purpose-specific variable such as `BRAIN` or `ROOT`. A changed `HOME` can make
the child tool load a different configuration and silently select the wrong
provider or credentials.

## Required report

For every recorded solve, preserve:

```text
challenge key
candidate flag
evidence kind: live-response | artifact
verifier: manifest hash | flagCheck | response/artifact excerpt
verbatim evidence excerpt
retry count and any rejected candidates
```
