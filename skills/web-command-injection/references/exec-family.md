# Exec Family — the per-language exec API catalog

## The API shape matters — shell vs argv vs eval

Three API families:

| Family | Form | Injection |
|---|---|---|
| shell-string | `exec("cmd "+x)` / `os.system("cmd "+x)` | separators |
| argv-array | `exec([cmd,x])` / `subprocess.run([cmd,x])` | flag-injection |
| evaluator | `eval(x)` / `exec(x)` / `new Function(x)` | code |

## PHP — the exec-family map

```php
system($cmd)                    — shell-string — stdout to response
exec($cmd,$out,$ret)            — shell-string — captured-array
passthru($cmd,$ret)             — shell-string — raw stdout
shell_exec($cmd)                — shell-string — full stdout
`$cmd`                          — shell-string — shell_exec
popen($cmd,'r')                 — shell-string — stream
proc_open($cmd,$desc,$pipes)    — shell-string — fd-map
proc_open([$cmd,$arg],$desc)    — argv-array — php7.4+ — safe
pcntl_exec($cmd,$args,$env)     — exec-replace
expect_popen($cmd)              — expect-lib
posix_kill(posix_getpid(),SIGKILL) — signal
posix_setuid(0)                 — uid-set
eval($x)                        — evaluator — php-code
assert($x)                      — evaluator — php<7
create_function('',$x)          — evaluator — php<7.2
call_user_func($f,$args)        — callable
call_user_func_array($f,$args)
$x()                            — var-function
preg_replace('/x/e',$x,$s)      — eval-per-match — php<5.5
mb_ereg_replace($p,$x,$s,'e')   — mb-e
include $x                      — include-path — different bug
require $x
```

## Python — the exec-family map

```python
os.system(x)                          — shell-string — returns exit-code
os.popen(x)                           — shell-string — stream
os.popen(x,'r').read()                — read
os.popen2/os.popen3/os.popen4         — legacy
commands.getoutput(x)                 — py2 — captured
commands.getstatusoutput(x)           — py2
subprocess.call(x,shell=True)         — shell=True — BUG
subprocess.check_call(x,shell=True)
subprocess.check_output(x,shell=True)
subprocess.run(x,shell=True,capture_output=True)
subprocess.Popen(x,shell=True,stdout=PIPE)
subprocess.call([cmd,x])              — argv-array — SAFE
subprocess.run([cmd,x])               — argv-array — SAFE
subprocess.Popen([cmd,x])             — argv-array — SAFE
subprocess.call(x,shell=True)         — the shell=True form — BUG
subprocess.run('ping '+x,shell=True)  — concat+shell=True
os.execvp('sh',['-c',x])              — sh -c
os.execv(cmd,[x])                     — argv — safe
os.execve(cmd,[x],env)
os.execle/execl/execlp/execlpe/execv/execve/execvp/execvpe
pty.spawn(x)                          — pty-shell
pty.fork()                            — pty-fork
eval(x)                               — python-eval
exec(x)                               — python-exec
compile(x,'','exec');exec()           — compile-eval
__import__('os').system('id')         — the bypass-one-liner
getattr(__import__('os'),'system')('id')
globals()['__builtins__']['eval'](x)
builtins.eval(x)
importlib.import_module('os').system('id')
```

## Node — the exec-family map

```javascript
require('child_process').exec('cmd '+x)           — shell-string
require('child_process').execSync('cmd '+x)
require('child_process').execSync('cmd '+x).toString()
require('child_process').execFile('cmd',[x])      — argv — SAFE
require('child_process').execFile('sh',['-c','cmd '+x])  — sh -c
require('child_process').spawn('cmd',[x])         — argv — SAFE
require('child_process').spawn('cmd',[x],{shell:true})   — shell:true — BUG
require('child_process').spawn('sh',['-c','cmd '+x])
require('child_process').fork('cmd',[x])          — node-fork — js-file
require('child_process').execFileSync('cmd',[x])
require('child_process').spawnSync('cmd',[x],{shell:true})
require('child_process').exec('ping '+x,(e,so,se)=>{})
eval(x)                                           — js-eval
new Function(x)                                   — js-eval
new Function('x',x)                               — js-eval
vm.runInThisContext(x)                            — vm-eval
vm.runInNewContext(x)                             — vm-eval
vm.Script(x).runInThisContext()
process.mainModule.require('child_process').execSync('id')
global.process.mainModule.require('child_process').execSync('id')
this.process.mainModule.require('child_process').execSync('id')
```

## Ruby — the exec-family map

```ruby
`cmd #{x}`                            — backtick — shell-string
%x{cmd #{x}}                          — shell-string
%x[cmd #{x}]
%x(cmd #{x})
system("cmd #{x}")                    — shell-string
system("cmd", x)                      — argv — SAFE
system("cmd", "arg", x)               — argv — SAFE
exec("cmd #{x}")                      — shell-string — replaces
spawn("cmd #{x}")                     — shell-string
spawn("cmd", x)                       — argv — SAFE
IO.popen("cmd #{x}")                  — shell-string — stream
IO.popen(["cmd",x])                   — argv — SAFE
Open3.popen3("cmd #{x}")              — shell-string
Open3.capture3("cmd #{x}")
Open3.capture2("cmd #{x}")
Open3.capture2e("cmd #{x}")
PTY.spawn("cmd #{x}")                 — pty
eval(x)                               — ruby-eval
eval("system(#{x})")                  — eval-injection
instance_eval(x)
class_eval(x)
module_eval(x)
Kernel.system("cmd #{x}")
Kernel.exec("cmd #{x}")
Kernel.spawn("cmd #{x}")
Kernel.`("cmd #{x}")                  — Kernel.` backtick-method
Process.spawn("cmd #{x}")
Process.spawn("cmd",x)                — argv
```

## Java — the exec-family map

```java
Runtime.getRuntime().exec("cmd "+x)            — shell-string-ish (tokenizes)
Runtime.getRuntime().exec(new String[]{"cmd",x}) — argv — SAFE
Runtime.getRuntime().exec("cmd /c "+x)         — cmd-string
Runtime.getRuntime().exec("sh -c "+x)          — sh-string
Runtime.getRuntime().exec(new String[]{"sh","-c","cmd "+x}) — sh -c argv
new ProcessBuilder("cmd "+x).start()           — splits
new ProcessBuilder("cmd","arg",x).start()      — argv — SAFE
new ProcessBuilder("sh","-c","cmd "+x).start() — sh -c
new ProcessBuilder("cmd","/c","cmd "+x).start() — cmd /c
new ProcessBuilder().command("sh","-c","cmd "+x).start()
Runtime.getRuntime().exec(String[])
Runtime.exec(String[])                          — deprecated
Process p = Runtime.getRuntime().exec("cmd "+x)
```

The `Runtime.exec(String)` form tokenizes on whitespace — `x` becomes
part of the command — separators still split inside `"cmd "+x`.

## .NET — the exec-family map

```csharp
Process.Start("cmd","/c "+x)              — cmd-string
Process.Start("sh","-c "+x)               — sh-string
Process.Start("cmd","/c","arg",x)         — argv — SAFE
Process.Start("cmd", "/c cmd "+x)         — cmd /c
new ProcessStartInfo{FileName="cmd",Arguments="/c "+x}
new ProcessStartInfo{FileName="cmd",Arguments="/c","arg",x}
System.Diagnostics.Process.Start
Diagnostics.Process.Start
```

## Go — the exec-family map

```go
exec.Command("sh","-c","cmd "+x).Run()        — sh -c — BUG
exec.Command("cmd",x).Run()                   — argv — SAFE
exec.Command("cmd","arg",x).Run()             — argv — SAFE
exec.Command("cmd","/c","cmd "+x).Run()       — cmd /c
exec.Command("sh","-c","cmd "+x).Output()
exec.CommandContext(ctx,"sh","-c","cmd "+x)
exec.Cmd{Path:"cmd",Args:[]string{"arg",x}}   — argv
syscall.Exec("cmd",[]string{"arg",x},env)     — exec-replace
syscall.Exec("sh",[]string{"-c","cmd "+x},env)
os.StartProcess("cmd",[]string{"arg",x},...)
```

## Perl — the exec-family map

```perl
`cmd $x`                              — backtick — shell-string
qx{cmd $x}                            — shell-string
qx(cmd $x)
system("cmd $x")                      — shell-string
system("cmd",$x)                      — argv — SAFE
system("cmd","arg",$x)                — argv — SAFE
exec("cmd $x")                        — shell-string
exec("cmd",$x)                        — argv — SAFE
open(F,"cmd $x|")                     — pipe-open — shell-string
open(F,"cmd","$x|")                   — multi-arg open — argv-ish
open(F,"-|","cmd",$x)                 — fork-open — argv — safe
open2(F,"cmd",$x)                     — IPC::Open2 — argv
open3(F,"cmd",$x)                     — IPC::Open3
IPC::Run::run(["cmd",$x])             — argv
IPC::Run::run("cmd $x")               — shell-string
eval $x                               — perl-eval — string-eval
eval "system(\"$x\")"                 — eval-injection
do $x                                 — do-file — file-exec
require $x                            — require-file
use $x                                — use-module
```

## C — the exec-family map

```c
system(buf)                     — buf is the command-string — BUG
popen(buf,"r")                  — the string is the command — BUG
execl("/bin/sh","sh","-c",buf,NULL)  — sh -c — BUG
execlp("sh","sh","-c",buf,NULL)
execv("/bin/sh",argv)           — argv — safe
execvp(cmd,argv)
execve(cmd,argv,env)
execle(cmd,...,env)
execl(cmd,"arg",x,NULL)
execlp(cmd,"arg",x,NULL)
execlpe
fexecve(fd,argv,env)
posix_spawn(&p,"/bin/sh",NULL,NULL,argv,env)   — argv
posix_spawnp
vfork();execv()                  — vfork+exec
fork();execv()                   — fork+exec
clone();execv()
```

## The "the sink is a string OR an array" — the boundary rule

- `system("cmd "+x)` / `exec("cmd "+x)` / `os.system("cmd "+x)` /
  `exec("cmd "+x)` — the string is the shell-line — SEPARATOR injection
- `execFile("cmd",[x])` / `subprocess.run(["cmd",x])` /
  `ProcessBuilder("cmd",x)` — the list is argv — FLAG injection only
- `eval(x)`/`exec(x)`/`new Function(x)` — the input is CODE — eval-injection

## The `shell=True`/`shell:true`/`sh -c`/`cmd /c` — the explicit-shell flag

- `subprocess.run(x,shell=True)` — `shell=True` makes the string a shell-line
- `spawn(cmd,args,{shell:true})` — `shell:true` same
- `exec.Command("sh","-c",x)` — `sh -c` same
- `Process.Start("cmd","/c "+x)` — `cmd /c` same

The presence of `sh -c`/`cmd /c`/`shell=True`/`shell:true` in source is
the strongest white-box marker.

## The "the output goes where" — stdout vs stderr vs exit-code vs stream

- `system()` → stdout + exit-code
- `exec()` → last-line / `$out[]` / exit-code
- `passthru()` → raw stdout
- `shell_exec()` / `` ` `` → full stdout
- `popen()` → stream — `fread`/`fgets`
- `proc_open()` → fd-pipes — `stream_get_contents($pipes[1])`
- `execSync()` → Buffer/stdout
- `exec()` → callback-err/stdout/stderr
- `spawn()` → stream-events
- `os.system()` → stdout + exit
- `os.popen()` → stream
- `subprocess.check_output()` → bytes
- `subprocess.run(capture_output=True)` → CompletedProcess.stdout/.stderr
- `` ` ``/`qx{}`/`%x{}`/`IO.popen` → string/stream
- `Process.getInputStream()` → stream

## Falsifiers

- the sink is argv-array AND the binary has no useful flag — dead
- the evaluator exists but the input is sanitized to a non-evaluable
  subset — dead

## Output to record

- which API family + which form carried the injection
