# Evidence Rules — what counts and what doesn't

## The standard — `AGENTS.md`'s proof rule

A flag counts only when it is read from a **live response or a supplied
artifact**. A flag-shaped string that has not passed
`tools/hooks.py pre-flag` is a *candidate*, not a flag. Command output
must be **in** the response — never asserted.

## What proves command injection — the class evidence

`--evidence-kind class` — the response bytes that prove a command ran:

- `uid=33(www-data) gid=33(www-data) groups=...` — `id` output
- `root`/`nt authority\system`/`WIN-ABC123` — `whoami`/`hostname`
- `Linux version`/`GNU`/`Darwin` — `uname`/`ver` output
- `Directory: `/`Mode`/`Length` — PS `dir`
- `total N`/`drwx` — `ls` output
- the verbatim flag `{...}` — impact evidence
- a timing DELTA ≥ threshold with a control — blind evidence

Each must be a verbatim substring of `--response` — the gate checks.

## What does NOT prove it

- the payload reflected back — `x;id` shown as `x;id` — reflection
- a 500/`SyntaxError` without exec output — an evaluator errored, not
  a command ran (route to eval-injection)
- `ping: x;id: not found` — the whole arg was argv — arg-injection
- a `Connection refused`/`timeout` — never a confirm
- "the tool would have shown" / "the command would have run" — a
  command not run is not evidence
- a flag-shaped string you typed, or from a writeup, or `flag{test}` —
  candidates until `pre-flag` passes

## The verbatim rule — the substring check

`--evidence` is asserted as a substring of `--response`. `uid=33` is
not `uid=3` — the bytes must match exactly. Hand-pasting a paraphrase
fails the gate; use `http_probe`'s emitted command.

## The blind-evidence standard

`sleep 5` → measure `t_before`/`t_after` — the evidence is the DELTA
with a `sleep 0` control. `oob_listener` log lines — the callback's
verbatim entry. `echo x>/tmp/o` then `?f=/tmp/o` — the fetched content.

## The flag rule — `pre-flag` before it counts

`flag{...}` seen in a response →
`python3 tools/hooks.py pre-flag <n> --value 'flag{...}'` → then
`post-probe --verdict confirms --evidence-kind impact --evidence
'flag{...}' --response '...'`. Never record a flag-shaped string
without the pre-flag check.

## The negative-evidence rule — a failed probe is data

- `;id` failed → `;` filtered OR shell absent — note which
- `|id` failed → `|` filtered OR argv-form
- `$(id)` failed → substitution filtered OR no shell
- record each: `--verdict refutes`/`inconclusive` with the observed
  constraint — feeds `error-analysis.md`'s map

## The artifact rule — when the response IS the file

A file-write-then-fetch `?f=/tmp/o` — the fetched `o` content is the
artifact. An OOB callback's log line is the artifact. Both are
"live response or supplied artifact" — quote verbatim.

## The chain-evidence rule — cmdi reaching a flag

The flag IS the impact evidence — but the chain that got there
(separator → shell → read path) is the `class` evidence. Record both.

## Falsifier-side evidence — what kills the class

`post-probe --verdict refutes` with the observed constraint:

- `the value never reaches an exec` (white-box confirmed)
- `every separator is stripped/rejected` (filter measured)
- `the sink is argv-form` (execFile/argv — error named)
- `no evaluator accepts the markers` (`7*7` literal)

## The record-format — what `--evidence` looks like

```
--evidence 'uid=33(www-data) gid=33(www-data)'     — verbatim
--evidence 'flag{cmd1nj3ct_m4st3r}'                — verbatim
--evidence 'elapsed 5.2s vs control 0.1s'          — the delta
--evidence 'OOB hit GET /x uid=33'                 — the log line
```

## Output to record

- the verbatim `--response` bytes + the `--evidence` substring + the
  channel (stdout/blind/oob)
