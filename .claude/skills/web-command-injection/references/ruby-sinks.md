# Ruby Sinks — system, backticks, Open3, eval

## The sink table

| Call | Shell? | Notes |
|---|---|---|
| `system(cmd)` | sh -c if string has shell chars | "magic" — see below |
| `system(cmd, arg)` | NO shell | argv form |
| `system([cmd, argv0], arg...)` | NO shell | explicit argv0 |
| `` `cmd` `` (backticks) | sh -c | always shell |
| `%x{cmd}` | sh -c | always shell |
| `exec(cmd)` | sh -c if string | replaces process |
| `spawn(cmd)` | sh -c if string | |
| `IO.popen(cmd)` | sh -c if string | |
| `Open3.popen3(cmd)` | sh -c if string | |
| `Open3.capture3(cmd)` | sh -c | |
| `eval(str)` | ruby eval | `eval-injection.md` |
| `instance_eval`/`class_eval`/`module_eval` | ruby eval | |
| `send`/`public_send`/`method()` | dynamic dispatch | `.send(:system, 'id')` |
| `Kernel.system`/`.exec`/``. | same as above | |
| `PTY.spawn` | sh -c | terminal spawn |
| `Process.spawn` | same as spawn | |

## The Ruby "magic" — when `system(str)` uses a shell

Ruby checks the string for shell metacharacters — `system("ping x;id")`
runs `sh -c` because it sees `;`; `system("ping", "x;id")` uses argv —
the `;` lands in argv[1] dead.

**The boundary: string with metachars → shell; separate args → argv.**

Metachars that trigger shell: `*?{}[]<>()~&|\\$;\x00\n` and backtick —
if your injection contains ANY of these, shell mode engages — even
mid-string.

## `%x{ }` and backticks — always a shell

`` `ping #{host}` `` / `%x{ping #{host}}` — string interpolation `#{...}`
INSIDE backticks — the interpolation is Ruby-side; the result is shell.
`host = 'x;id'` → `` `ping x;id` `` → exec.

## `eval` — the Ruby-evaluator sink

```ruby
eval("system('id')")
eval(params[:code])
```

`eval` runs Ruby — the payload is Ruby code. `ERB.new(x).result` —
ERB templates are eval too — `<%= system('id') %>` — `web-ssti` overlap
boundary: ERB-as-template is ssti; ERB-as-eval is cmdi — same class by
chain-card logic (evaluator).

## Dynamic dispatch — `send` chains

```ruby
klass.send(params[:m], params[:a])        — m=:system → exec
obj.public_send(m, *args)
Object.const_get(params[:k]).new(params[:a])
```

`send` with a method name param → `m=system` exec — `m=` gets the method
name string, `a` the arg.

## `Open3`/`PTY` — stream-control exec

```ruby
Open3.popen3("ping #{host}")
Open3.capture3("ping " + host)
```

Same string→shell rule. `Open3.pipeline` chains.

## `exec` vs `system` vs `spawn` — return differences

- `exec` REPLACES the process — the app dies into your command (output
  still shows if stdout inherited)
- `system` returns true/false/nil
- backticks return stdout string
- `spawn` returns pid — async, no output

For evidence, backticks/`%x{}` output is visible if the app renders it.

## The `#{...}` interpolation is RUBY-side — check who interpolates

`` `ping #{var}` `` — `#{var}` expands in Ruby BEFORE the shell sees it
— the shell sees the expanded string. Injection inside `#{var}` targets
the SHELL; injection INTO the literal (eval'ing the source) targets Ruby.

## Falsifiers

- `system(cmd, arg)` multi-arg argv form AND no backtick/%x{}/eval/send
  sink
- input never contains shell metachars reaching the string form

## Output to record

- the sink + string-vs-argv form + whether interpolation is the injection
