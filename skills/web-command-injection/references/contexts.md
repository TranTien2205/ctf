# Contexts — the injection-surface taxonomy

## The five canonical shapes

| Shape | Sink | Injection form |
|---|---|---|
| shell-string | `system("cmd ".$x)`/`sh -c`/`cmd /c` | separators `$()`/backtick |
| argv-element | `execFile('ping',[x])`/`subprocess.run([cmd,x])` | flag-injection |
| evaluator | `eval($x)`/`exec($x)`/`new Function`/`Runtime.exec` | code payload |
| filename | `convert "$f"`/`tar xf "$f"`/`unzip "$f"` | filename-meta |
| arg-name | `system("ping ".$opt)`/tool-flag position | flag-injection |

## Shell-string — the classic

`system('ping '.$host)` — `host` concatenated → `;id` runs.

- `system()`/`popen()`/`shell_exec()`/`exec()`/`passthru()`/`proc_open()`
  in PHP
- `os.system()`/`os.popen()`/`commands.*`/`pty.spawn`/`subprocess.*(shell=True)`
  in python
- `exec()`/`execSync()`/`spawn(cmd,{shell:true})`/`execFile(file,{shell:true},args)` in node
- `` `cmd` ``/`system()`/`exec()`/`%x{}`/`IO.popen()` in ruby
- `Runtime.exec(string)`/`ProcessBuilder("sh","-c",string)` in java
- `Process.Start("cmd","/c "+x)`/`Process.Start("sh","-c "+x)` in .net
- `system(string)`/`popen(string)`/`execvp("sh",["-c",x])`/`execlp("sh","-c",x)` in C
- `os/exec.Command("sh","-c",x)`/`syscall.Exec("sh",["-c",x])` in go
- `system(string)`/`` `cmd` ``/`qx{string}`/`open(F,string)`/`open2`/`open3`/`IPC::Run`/`String::ShellQuote` in perl
- `Process.run`/`Process.start`/`shell=true` in dart
- `os/exec.Cmd.Run`/`Command`/`Shell` in swift
- `shell-run`/`os.execute`/`io.popen` in lua
- `Process.run`/`Process.start`/`RunInShell`/`exec` in others

The `+`/`.`/`..`/`${}`/`#{}`/f-string/`%s`/`format`/`concat`/`join`/template-
literal that puts `x` INSIDE the command-string is the marker.

## argv-element — `execFile`/`spawn`-array/`ProcessBuilder`-list

The args are a LIST — no shell:

```python
subprocess.run(['ping', x])          # x is argv[1] — 'x;id' is ONE arg
subprocess.run(['sh','-c','ping '+x])# x concat'd INSIDE sh -c — BUG
```

The difference: `['ping',x]` vs `['sh','-c','ping '+x]` — `sh -c` is
the shell-boundary. Without it, `x` is one argv element — flag-injection
only: `x='--upload-pack=id'`/`x='-f/etc/passwd'`.

## Evaluator — `eval`/`exec`/`new Function`/compile/eval-string

`eval('echo '.$x)`/`eval($x)`/`new Function('x',...)`/`exec(compile(x))`/
`assert($x)`/`create_function`/`preg_replace('/x/e',...)`/

- the payload is CODE not shell — `system('id')`/`os.system('id')`/
  `execSync('id')` — `eval-injection.md`
- fingerprint with `7*7`/`phpversion()`/`process.version`/language-marker

## Filename — `convert "$f"`/`tar xf "$f"`/`file "$f"`/`exiftool "$f"`

- `f` is the file's NAME — the name carries `;id` — `filename-injection.md`
- the file's CONTENT is a separate surface — `imagemagick-deep.md`
- `f` argv-position + the tool's flag-injection — `arg-injection-deep.md`

## Arg-name/tool-name — `system($tool.' -fixed')`/`$tool` as the param

If `?tool=ping`/`?tool=id` selects the binary — the tool NAME is the
injection — `?tool=cat /flag`? — the space splits — `?tool=id`/`?tool=sh`
runs the binary.

## The secondary points — headers/cookies/stored/path/array

- `User-Agent`/`Referer`/`X-Forwarded-For`/`X-Real-IP`/`X-Client-IP` — logged
  → `log-poisoning.md`
- `Cookie`/`X-Custom-*` — if logged/exec'd
- path-segment `/ping/{x}` — `x` in the segment
- multipart `filename="x.png;id"` — filename
- JSON `"host":"x;id"` — the string-value inside
- `args[]` array — each element if shelled
- second-order stored field — `second-order.md`

## The distinguishing test — which shape is this?

| Send | Shell-string if | argv if | eval if |
|---|---|---|---|
| `x;id` | `uid=` in output | `ping: x;id: not found` | syntax-error |
| `x\|id` | `uid=` output | `ping: x\|id: not found` | error |
| `x$(id)` | `xuid=` output | literal | error |
| `x\`id\`` | `xuid=` output | literal | error |
| `x%0aid` | two commands | `ping: x%0aid` | error |
| `x'or'a` | — | — | `'or'` if php-eval |
| `x;echo PWN` | `x` then `PWN` | literal | error |
| `system('id')` | error | literal | php-eval runs |
| `7*7` | literal | literal | `49` if eval |

## Falsifiers

- no shape accepts ANY form → the surface isn't an exec boundary —
  check `denied-conditions.md`

## Output to record

- which shape + which byte carried the injection
