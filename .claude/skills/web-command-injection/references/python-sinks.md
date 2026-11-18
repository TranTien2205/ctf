# Python Sinks — os.system, subprocess, eval

## The sink table

| Call | Shell? | Notes |
|---|---|---|
| `os.system(cmd)` | `/bin/sh -c` | sync, no capture |
| `os.popen(cmd)` | `/bin/sh -c` | returns pipe obj |
| `subprocess.run(cmd, shell=True)` | `/bin/sh -c` | most common modern |
| `subprocess.call/check_call/check_output(..., shell=True)` | `/bin/sh -c` | output per variant |
| `subprocess.Popen(cmd, shell=True)` | `/bin/sh -c` | |
| `subprocess.run([cmd, arg])` | NO shell | argv — falsifier at this sink |
| `subprocess.run('cmd '+x, shell=True)` | sh -c | string concat — THE bug |
| `subprocess.run([cmd, x], shell=True)` | sh -c weird | shell gets `cmd`, `x` becomes `$0`! |
| `os.exec*` family | NO shell | replaces image, argv |
| `os.spawn*` | NO shell | argv variants; `spawnl` etc |
| `commands.getoutput`/`getstatusoutput` | sh -c | legacy |
| `eval(expr)` | python eval | `eval-injection.md` |
| `exec(code)` | python exec | |
| `compile`+`exec` | python eval | |
| `os.system` inside `eval`/`exec` | python eval → os.system | chained |
| `pty.spawn` | shell spawn | interactive |
| `asyncio.create_subprocess_shell` | sh -c | async version |
| `os.write`/pipes | no | fd-level |
| `subprocess.run([...], executable='/bin/bash')` | bash -c | the `executable=` override! |

## The `shell=True` + list trap — the subtle one

```python
subprocess.run(['ping', user_input], shell=True)
```

With `shell=True` + a list: `[0]` becomes the command string, `[1:]`
become `$0`, `$1`... to the shell — `user_input` becomes `$0`, not an
arg! The command run is just `ping` (no arg) with `$0=user_input`. The
injection point is argv[0] of the shell, not the command line.

This is the missed-boundary bug — looks injectable, isn't via the string.

## `shell=True` + string concat — the bug

```python
subprocess.run('ping -c1 ' + host, shell=True)
subprocess.run(f'ping -c1 {host}', shell=True)
subprocess.run('ping -c1 %s' % host, shell=True)
```

Classic. `host='127.0.0.1;id'` → `ping -c1 127.0.0.1;id`.

## `executable=` — changing the shell

`subprocess.run(cmd, shell=True, executable='/bin/bash')` — bash instead
of sh — bash-only syntax now works (`{a,b}`, `<()`, arrays).

## `os.system`/`os.popen` — always sh -c

```python
os.system('ping -c1 ' + host)
os.popen('ping -c1 ' + host).read()
```

Old-style — always a shell. The injected `;`/`|`/`&&`/`$()`/`backtick`
all work in `/bin/sh` (dash on Debian/Ubuntu — `shell-differences.md`).

## `eval`/`exec` — the python-evaluator sinks

```python
eval('__import__("os").system("id")')
exec('import os;os.system("id")')
eval(input)  — the classic eval(input()) trap
```

If eval's globals are sandboxed (`eval(x, {'__builtins__':{}})`) — the
`().__class__.__base__.__subclasses__()` gadget chain escapes —
`eval-injection.md` has the full gadget tree.

## `code.InteractiveConsole`/`code.interact` — REPL exposure

Debug endpoints exposing `code.interact`/`InteractiveConsole` — direct
python exec — sometimes hit via a `/console` route (Werkzeug debugger!).

Werkzeug debug console — the `?__debugger__=yes&cmd=...` endpoint —
PIN-protected usually but the PIN can be brute-forced/derived
(compute from `/proc/sys/kernel/random/boot_id` etc — the classic
werkzeug-console chain).

## `os.exec*`/`spawn*`/`fork` — argv-only

`os.execvpe`, `os.spawnlp` — replace/spawn without shell — metachars
dead; `argument-injection.md` only.

## `subprocess.run(input=...)` — stdin-carried commands

The input feeds the command's stdin — `sh`/`python -`/`bash` as the
fixed command reads stdin → the stdin payload IS the code.

## Command-lookup order — `shutil.which`

`subprocess.run(['mycmd', x])` — `mycmd` resolved via PATH — `PATH`
control + writable dir → shadow — `env-var-injection.md`.

## Python version quirks

- `os.system` always `/bin/sh` on POSIX regardless of $SHELL
- `subprocess` `shell=True` default `/bin/sh`, `executable=` changes it
- `shlex.quote`/`shlex.join` — real escaping when used — falsifier signal
- `pipes.quote` (deprecated) — same

## The `eval`/`exec`→`os.system` bridge — python code reaching shell

Inside `eval`/`exec`, `__import__('os').system('id')` — the bridge
payload — `eval-injection.md` for the sandbox-escape ladder.

## Falsifiers

- `subprocess` argv-array with no shell=True AND input not reaching
  argv[0] position AND no eval/exec/InteractiveConsole sink
- `shlex.quote`/`shlex.join` used correctly

## Output to record

- the sink call form + `shell=` value + the argv layout if list-form
