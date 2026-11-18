# Perl & Other Sinks — system, backticks, open pipes, and the rest

## Perl sink table

| Call | Shell? | Notes |
|---|---|---|
| `` `cmd` `` backticks | sh -c | always shell |
| `qx/cmd/` | sh -c | same |
| `system($cmd)` single scalar | sh -c IF metachars | like Ruby — magic check |
| `system($cmd, @args)` | NO shell | argv |
| `system {$cmd} @args` | NO shell | explicit argv0 |
| `exec($cmd)` | sh -c if metachars | replaces |
| `open(F, "cmd \|")` / `open(F,"\|cmd")` | sh -c | pipe-open — `open(FILE,'|id')` execs |
| `open(F,"cmd|")` trailing pipe | sh -c | write-to-process |
| `IPC::Open3::open3` | depends | |
| `IPC::Open2`/`open2` | sh -c with string | |
| `eval $str` | perl eval | `eval-injection` |
| `do 'file'`/`require` | file eval | perl code |
| `readpipe` | sh -c | internal backtick |

## The `open(F,'|cmd')` primitive — underrated

```perl
open(F, "ping $host |")   — host injectable → shell
open(F, "| ping $host")   — write direction
open(F, "-|")             — fork/exec argv form — argv boundary
open(F, "|-")             — same
open(F, "-|", 'cmd', @args) — list form — argv, no shell
```

3-arg open with `-|`/`| -` is the safe form — argv mode. The 2-arg
string form with `|` is the shell sink.

## Perl magic — same metachar detection as Ruby

`system("cmd $x")` with `x` containing `;` → sh -c. `system("cmd", $x)`
→ argv.

## `eval`/`do`/`require` — perl code exec

`eval { $code }`/`eval $str`/`do $file`/`require $file`/`use` — perl
code sinks. `use Safe` compartment is a restricted eval — bypassable.

## Other sinks worth knowing

### Go

```go
exec.Command("sh","-c", cmd).Run()     — sh -c — injectable
exec.Command("ping", host).Run()        — argv — dead for metachars
exec.Command("cmd","/C",cmd)            — windows shell
syscall.Exec                            — replace
```

`exec.Command(name, args...)` — argv — `argument-injection.md`.
`shell:true` equivalent doesn't exist — shell must be explicit.

### C / native

```c
system(cmd)          — /bin/sh -c
popen(cmd, "r")      — /bin/sh -c
execv* family        — argv
execlp/execl("sh","sh","-c",cmd,NULL)  — shell
```

`system()`/`popen()` always shell.

### Lua

```lua
os.execute(cmd)      — sh -c
io.popen(cmd)        — sh -c
load(str)            — lua eval
```

### Bash-native — a `.sh` script's `$var`

A CGI/.sh script: `ping $host` unquoted → injection. If quoted
`ping "$host"` → `$( )`/backtick still expand → `quoting.md`.

### Rust

```rust
Command::new("sh").arg("-c").arg(cmd)     — shell
Command::new("ping").arg(host)            — argv
```

### .NET

```csharp
Process.Start("cmd","/c "+x)              — cmd shell
ProcessStartInfo{FileName="sh",Arguments="-c "+x}
Process.Start("ping",x)                   — argv
```

### CGI / shell-cgi — the CGI-script shape

A `.sh` CGI or a bash CGI — the request fields become env vars —
`HTTP_USER_AGENT`→`$HTTP_USER_AGENT` inside the script — `eval`/`system`
on it → `env-var-injection.md`.

### Erlang/Elixir

```elixir
System.cmd("sh",["-c",cmd])   — shell
System.cmd("ping",[host])      — argv
:os.cmd(string)               — port program, sh -c
```

### Haskell

```haskell
System.Process.callCommand str   — shell
createProcess (shell str)         — shell
rawSystem cmd args                — argv
```

## The pattern — every language has the same dichotomy

```
STRING passed to interpreter-with-shell  → sh -c → injectable
ARGV ARRAY passed to exec-family         → no shell → falsifier, check flags
```

The boundary question is universal — `detection.md` covers probing it.

## Falsifiers

- every sink is argv-form AND the fixed commands take no exec-capable
  flag

## Output to record

- the language + sink signature + which side of the boundary
