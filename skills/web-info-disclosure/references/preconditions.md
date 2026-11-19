# Preconditions — check before each channel

| Channel | Must be true | Check |
|---|---|---|
| .git recovery | HEAD serves 'ref:' AND objects serve | HEAD + one object path |
| config leak | the body is real KEY=VALUE, not catch-all | baseline diff |
| archive | response has archive magic | file -b / unzip -l |
| source maps | a map exists or a sibling resolves | sourceMappingURL or <name>.map 200 |
| debug surface | the debug page's real renderer answers | framework-styled page |
| verbose errors | errors carry internals, not a branded page | trigger + read body |
| autoindex | 'Index of' structure present | body pattern, not 200 |
| status/metrics | the page is a real status/metrics body | format check |
| logs served | the file reads as log lines | content shape |
| source disclosure | the file serves raw code, not executed output | source text present |
| comments | comments beyond boilerplate exist | grep <!-- --> |
| 403 bypass | the artifact exists behind the rule | verb/Host/path tricks flip it |
| timing oracle | distributions separate at 50+ samples | measure, don't assume |

## The universal precondition

The catch-all baseline exists and is measured. Without it, no positive
answer means anything — the first request of any session.

## Checking cheaply

The precondition checks ARE the first probes: HEAD for .git, a status
request for ops surfaces, a bad-type input for verbose errors. A channel
whose precondition probe fails costs one request — never more before the
channel's own sweep starts. A precondition that fails is a closed channel,
recorded as a negative in `../field-notes.md` with the probe that closed
it; the class is still open while any channel's precondition holds.

## Order

Baseline → headers → high-value paths (.git, .env, robots, backup) → ops
surfaces → variants → 403-bypass attempts → hint-driven probes. Each step
costs more than the last; the cheap checks decide whether the expensive
ones run at all — that ordering is the whole point.


