# Environment Variable Injection — the invisible argv

## The primitive — env vars travel with the exec

`subprocess.run(..., env=...)`, `putenv()`, `SetEnvironmentVariable`,
`CGI`'s HTTP-header-to-env mapping — any path where a request value
becomes an env var the spawned process inherits.

## The classic CGI mapping — `HTTP_*` env vars

CGI scripts get headers as env vars: `HTTP_USER_AGENT`,
`HTTP_X_FOO` from `X-Foo` header. A shell script doing `eval $HTTP_X`
or `system("echo $HTTP_UA")` — the header is the injection vector —
`detection-contexts.md`'s header surface.

## High-value env vars to control

| Var | Effect | Exec path |
|---|---|---|
| `LD_PRELOAD` | load .so first | write .so + set var → exec at ANY process start |
| `LD_LIBRARY_PATH` | lib search path | lib shadowing |
| `LD_AUDIT` | audit interface | loads lib at link |
| `PATH` | command search | shadow `cat`/`id` with your script |
| `IFS` | field split char | `[a-z]` IFS splits command names weirdly |
| `BASH_ENV`/`ENV`/`ZDOTDIR` | startup files | `sh`/`bash` reads it at start → exec |
| `PYTHONPATH`/`PYTHONSTARTUP` | module path/startup | module shadowing/startup exec |
| `PYTHONINSPECT` | drop to REPL | interactive py at exit |
| `PERL5OPT`/`PERL5LIB` | perl flags/lib path | `-Mmodule` auto-load |
| `RUBYOPT`/`RUBYLIB` | ruby flags | `-r` auto-require |
| `NODE_OPTIONS` | node flags | `--require=x` preload module |
| `GIT_SSH_COMMAND` | git's ssh cmd | runs at fetch |
| `TAR_OPTIONS`/`WGETRC`/`CURL_HOME`/`PSQL_OPTIONS` | tool opts | inject flags past `--` |
| `SHELL`/`TERM`/`EDITOR`/`PAGER`/`VISUAL` | program names | editors/pagers launched with these |
| `HTTP_PROXY`/`http_proxy` | proxy | mitm the app's outbound |
| `LD_DEBUG` | debug output | info leak |
| `IFS` abuse | `IFS=x` — field split on 'x' | `catx/flag` splits at `x` → `cat /flag` |

## `LD_PRELOAD` — the strongest env primitive

Write a `.so` (via upload), set `LD_PRELOAD=/path/x.so` in env — ANY
dynamically-linked binary starts running your `__attribute__((constructor))`
at load. Classic persistence + exec.

## `BASH_ENV`/`ENV` — the startup-file exec

`BASH_ENV=/path/script bash -c 'anything'` — bash sources BASH_ENV for
non-interactive shells — `sh`/`dash` honor `ENV`. If you control env
input and the app spawns ANY shell — exec.

## `IFS` custom — a different whitespace

`IFS=x; catx/flag` → IFS='x' splits `catx/flag` into `cat` `/flag`.
Weird but works: IFS=`a` splits on 'a' chars — `c-at` no... IFS must be
a char in the string: `cXt` with `IFS=X` → `c` `t` — wrong split.
`caxt` with IFS=`a`? `c` `t`. Hmm — IFS splits at the IFS CHAR:
`catX/flag` doesn't help — need `cXt` where X is the IFS char:
`IFS=X;cXtX/flag` — splits at `X` → `c`,`t`,`/flag` — wrong. Right form:

```
IFS=,;cat,/flag  → "cat" "/flag"? — no: `cat,/flag` splits at `,` →
  words "cat" "/flag" — YES that works: IFS=,;cat,/flag → cat /flag
```

Wait — `IFS=,;` sets IFS to `,` for the current shell, then `cat,/flag`
splits at `,` into `cat /flag`. Correct.

## `PATH` shadowing — replace a command the app runs

App runs `ping $host` — `PATH` determines which `ping`. If you can write
a file `/tmp/x/ping` (script: `#!/bin/sh\ncat /flag`) AND control `PATH=/tmp/x:$PATH` → your ping runs.

## CGI `QUERY_STRING`/`REDIRECT_STATUS`/`REDIRECT_...`

mod_cgi passes `REDIRECT_<header>` for internal redirects — PHP-CGI
`REDIRECT_STATUS=200` bypass for `cgi.force_redirect` — legacy but real
(`php-cgi-params` territory).

## The env-injection reach — where does env control come from?

- `putenv($_GET['k'].'='.$_GET['v'])` — direct env set (rare, CTF shape)
- CGI headers → `HTTP_*`
- `subprocess.run(..., env={**os.environ, **user_dict})` — merged env
- a config file/`docker env`/`.env` write — env via file
- `SetEnv`/`SetEnvIf` in `.htaccess` — Apache env via upload!

## `.htaccess` env set — `SetEnv LD_PRELOAD /path/x.so`

`SetEnv`/`SetEnvIf`/`PassEnv` in `.htaccess` — Apache runs CGIs/PHP with
that env — combined with an uploaded `.so` = exec. Requires mod_env +
`AllowOverride` covering it — `skills/web-file-upload/references/apache-deep.md`/`skills/web-file-upload/references/init-hooks.md`.

## Falsifiers

- no env-control path exists (no putenv, no CGI header flow, no env file)
- `secure_getenv`/sanitized env — `LD_PRELOAD` etc. stripped by loader
  for setuid or by the runtime

## Output to record

- which env var is controllable + through which carrier (header/field/
  file) + which process it reaches
