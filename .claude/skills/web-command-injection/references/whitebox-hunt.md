# White-box Hunt — reading the handout for the sink

## The grep pass — find every exec-shaped call

```bash
grep -rn 'system\|exec\|popen\|passthru\|shell_exec\|proc_open\|pcntl' src/
grep -rn 'os.system\|os.popen\|subprocess\|commands\.\|pty\.spawn' src/
grep -rn 'child_process\|execSync\|spawn\|exec(' src/
grep -rn 'Runtime\.\|ProcessBuilder\|Process\.Start\|Process\.exec' src/
grep -rn '`.*`\|%x{\|system(\|exec(\|open(.*|' src/
grep -rn 'eval\|assert\|create_function\|preg_replace.*\/e' src/
grep -rn 'sh -c\|bash -c\|cmd /c\|powershell' src/
```

## The sink-shaped call sites — what to look for per language

| Lang | Sink | Injection marker |
|---|---|---|
| PHP | `system("ping ".$x)` | concat'd var |
| PHP | `shell_exec($cmd)` | var-as-command |
| PHP | `exec("cmd ".$x)` | concat |
| PHP | `eval($x)` | whole-input eval |
| Python | `os.system(f"ping {x}")` | f-string concat |
| Python | `subprocess.run(f"ping {x}",shell=True)` | `shell=True` |
| Python | `eval(x)` / `exec(x)` | eval |
| Node | `exec("ping "+x)` | `+` concat |
| Node | `execFile('ping',[x])` | argv — NOT shell |
| Node | `eval(x)`/`new Function(x)` | eval |
| Ruby | `` `cmd #{x}` `` / `system("cmd #{x}")` | interpolation |
| Java | `Runtime.exec("cmd "+x)` | `+` concat |
| Java | `new ProcessBuilder("sh","-c","cmd "+x)` | sh -c |
| Go | `exec.Command("sh","-c","cmd "+x)` | sh -c |
| C | `system(buf)` where `buf` holds input | buffer concat |
| Perl | `system("cmd $x")` / `` `cmd $x` `` | interpolation |

## The `shell=True` / `sh -c` / `cmd /c` signature

- `subprocess.run("ping "+x, shell=True)` — `shell=True` is the flag
- `exec.Command("sh","-c",cmd)` — `sh -c` string → shell
- `exec.Command("ping",x)` vs `exec.Command("sh","-c","ping "+x)` —
  array vs shell — the FIRST is argv-safe, the SECOND is the bug
- `Process.Start("cmd","/c ping "+x)` — `/c` + concat → cmd injection
- `Runtime.exec("cmd /c ping "+x)` — same

## The distinction that matters — argv vs concat

| Safe | Unsafe |
|---|---|
| `execFile('ping',[x])` | `exec('ping '+x)` |
| `subprocess.run(['ping',x])` | `subprocess.run('ping '+x,shell=True)` |
| `exec.Command('ping',x)` | `exec.Command('sh','-c','ping '+x)` |
| `ProcessBuilder('ping',x)` | `ProcessBuilder('sh','-c','ping '+x)` |
| `pcntl_exec('/bin/ping',[x])` | `system('ping '.$x)` |

An argv-form sink has no shell — only `argument-injection.md` applies.

## The escaping/sanitizing calls — what the filter does

| Call | Does | Bypass |
|---|---|---|
| `escapeshellarg(x)` | wraps `'x'` | arg-injection only |
| `escapeshellcmd(x)` | escapes metachars | quoting-break |
| `addslashes(x)` | `\` quotes | arg-injection |
| `escapeshellarg`+concat | `'x'` + more | `'`-break then `;` |
| `str_replace(';','',x)` | strips ; | other sep |
| `preg_match('/[;&|]/')` | rejects metas | encoding |
| `intval`/`is_numeric` | numeric only | none — arg-injection |
| `basename`/`realpath` | path-clean | filename-injection |
| `sanitize-x` custom | whatever it does | read it |

## The flag-path hunt — where the flag is

```bash
grep -rn 'flag' src/ | head
grep -rn 'flag{\|FLAG\|flag.txt\|/flag' src/ | head
ls -la src/ flag* .env Dockerfile docker-compose* 2>/dev/null
cat Dockerfile docker-compose.yml .env 2>/dev/null | grep -i flag
```

## The reachable-surface check — which input reaches the sink

Trace backward from the sink: `system($cmd)` ← `$cmd = "ping ".$host` ←
`$host = $_GET['host']` — the input is `host`, the concat is the bug.

An input that's `intval()`'d / `preg_match`ed before the sink isn't a
valid probe target — the filter decides which bypass applies.

## The second-order path — stored → exec

`INSERT INTO jobs (cmd) VALUES ('$x')` then `system($row['cmd'])` — the
exec is in a different request — `second-order.md`.

## Falsifiers

- no exec-shaped sink exists → the class was never live — a classifier
  miss; record the kill
- every sink is argv-form → the class is arg-injection only

## Output to record

- the sink file:line + the input → concat path + the filter in between
