# popen/system/exec — why the sink signature decides the bug

## The three exec paradigms — universal across languages

```
A) shell-string:   run a STRING through a shell parser
B) argv-array:     run a program with argv[] directly — no parser
C) evaluator:      run the string as CODE in a language eval
```

Shell-string (A) → all metachar tricks live here.
argv-array (B) → only flag injection lives here — falsifier for `;|&$()`.
Evaluator (C) → the payload is source code of that language — the
chain-card widened this class to cover it.

## The identification table — output → sink form

| Observed | Implies |
|---|---|
| `sh: 1: X: not found` | sh -c (dash) — shell-string |
| `bash: X: command not found` | bash -c |
| `Syntax error: Unterminated quoted string` | shell parser — string |
| `Cannot run program "x;y": error=2` | Java argv — `;` inside argv |
| `No such file or directory: 'x;y'` | execv argv — `;` literal in argv |
| `Errno 2` python style | subprocess argv |
| `Command failed: ping ...` + command echoed | node exec — template leak |
| output contains `PING`, `traceroute`, `dig` headers | tool ran |
| output differs when separator added | shell present |

## `popen`/`system`/`exec` C-level — always sh -c

C `system()`/`popen()` call `sh -c` — period. `execv*` don't. In a CGI
binary or compiled tool, `system()` = shell, `execv` = argv.

## The "wrapper" trap — `sh -c` INSIDE a shell string

`exec('sh -c "ping '.$x.'"')` — nested shells, quoting gets messy —
`quoting.md`'s nested-quoting section.

## The `execFile`-with-args-array-is-still-not-safe caveat

`execFile('ping', [host])` is argv — BUT:

- host as flag (`-c`, `--`) → `argument-injection.md`
- host containing spaces does NOT split (argv elements don't re-split)
  — space-injection dead here
- BUT some tools' `execFile` accepts `shell:true` option — reopens it

## `subprocess` `shell=True`+list → the `$0` trap — `python-sinks.md`

`['cmd', x]` with `shell=True` → `x` is `$0` of the shell not an arg to
cmd — the injection point exists but is `$0` not the command args — if
the shell runs `sh -c cmd x`, `x` shows as `$0` only when `cmd` reads it.
Specific: `sh -c 'cmd' x` — `$0=x`, `cmd` runs with no arg. Injection
into `x` only execs if `cmd` itself shells `$0` — usually dead BUT the
`[0]` element is still shell-parsed — if the FIRST element is
controllable, injection.

## The `$0`-injection — `sh -c 'real-cmd' injected-arg`

`subprocess.run(['echo hi', userinput], shell=True)` →
`sh -c 'echo hi' userinput` → `userinput` is `$0`, invisible to echo —
DEAD. But if `cmd` were `$0`-expanding... edge case.

The REAL injection: `[0]` slot — `['ping '+x]` as one string → `x`
inside the shell string.

## `pcntl_exec`/`os.exec*`/`execv*` — process replacement

Replace the calling process image with the new program — argv only.
The OUTPUT goes to the same fds — the shell didn't parse anything.

## Signal: `sh -c` present → shell-differences apply

Once `sh -c` confirmed, determine WHICH sh:

- `/bin/sh` → symlink to `dash` (Debian/Ubuntu), `bash` (RHEL-ish),
  `busybox` (Alpine/containers)
- `sh` vs `bash` syntax differences → `shell-differences.md`

`echo $0`/`readlink /bin/sh`/`ls -l /bin/sh` tells you.

## The spawn-locale — which shell & which PATH

`sh -c` inherits the app's env — `PATH` may not include `/sbin`,
`/usr/local/bin` — `cat`/`id` usually fine, `nc`/`socat` maybe not —
`command -v x` or `which x` to check.

## Output to record

- sink paradigm (A/B/C) + the shell binary resolved + the argv layout
