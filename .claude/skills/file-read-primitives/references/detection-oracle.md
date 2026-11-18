# Detection Oracle — reading the app's own error for the mechanism

## The oracle model — the error IS the mechanism map

Every response — content, error, status, timing — is a signal about
WHERE the read happened and WHICH layer stopped it.

## Oracle 1 — the verbatim-content echo — `root:x:0:0:`

```
?file=/etc/passwd       → "root:x:0:0:root:/root:/bin/bash" → READ-WORKS
?file=C:\Windows\win.ini → "[fonts] [extensions]" → READ-WORKS-WINDOWS
```

The verbatim-content echo — the gold-standard — `evidence-rules.md` —
the class is confirmed.

## Oracle 2 — the `FileNotFound`-names-the-path

```
?file=/etc/passwd       → "File not found: /etc/passwd" → RESOLVER-WORKED-MISS
?file=/nonexistent      → "File not found: /nonexistent" → RESOLVER-TRIED
```

A `FileNotFound`/`No such file`/`ENOENT` naming YOUR path — the path
RESOLVED, the file is missing — the mechanism is LIVE — the file just
doesn't exist.

## Oracle 3 — the `open_basedir`-names-the-confine

```
?file=/etc/passwd → "Warning: open_basedir restriction in effect.
  File(/etc/passwd) is not within the allowed path(s): (/var/www/html:/tmp)"
```

`open_basedir` — the PHP-confine — the confine is REAL — the traversal-
ladder dies inside `/var/www/html:/tmp` — `/proc/self/root/` may escape.

## Oracle 4 — the `disable_functions`-names-the-kill

```
?file=php://input → "Warning: include() has been disabled for security reasons"
```

`disable_functions` — the exec-kill — `include`/`require`/`eval`/
`system`/`exec`/`shell_exec`/`passthru`/`popen`/`proc_open`/`pcntl_exec`
disabled — `file_get_contents` read survives.

## Oracle 5 — the `allow_url_*`-names-the-wrapper-kill

```
?file=php://input → "Warning: include(): URL file-access is disabled"
?file=data://x    → same — allow_url_include=Off
?file=http://x    → same — allow_url_fopen=Off
```

`allow_url_include`/`allow_url_fopen` — the wrapper-kill — `php://`/
`data:`/`phar://`/`zip://`/`glob://`/`expect://`/`ssh2.*`/`http://`/
`ftp://` all die — `file:///` survives.

## Oracle 6 — the `Permission denied`-names-the-perm

```
?file=/etc/shadow → "Permission denied" → exists-but-unreadable
?file=/etc/passwd → works → readable
```

`Permission denied` — the perm-confine — `/root/*`/`/etc/shadow` —
the file EXISTS, the uid/gid can't reach it — `Uid`/`Gid` from
`/proc/self/status` — the kill-map is the reachable-set.

## Oracle 7 — the `Is a directory`-names-the-listing-miss

```
?file=/etc        → "Is a directory" → dir-not-a-file
?file=/etc/       → "Is a directory" → dir-not-a-file
```

`EISDIR` — the read tried, the path is a dir — try `file:///etc/`-
listing (Java) or `glob:///*` or `scandir`-equivalent — a listing-
sink is a different primitive.

## Oracle 8 — the `File name too long`-names-the-length

```
?file=<4096-chars> → "File name too long" → ENAMETOOLONG
```

`ENAMETOOLONG` — the path-length limit — the path reached fs but is
too long — a length-oracle.

## Oracle 9 — the `Too many levels`-names-the-symlink-loop

```
?file=/x → "Too many levels of symbolic links" → ELOOP
```

`ELOOP` — a symlink-loop — the symlink-chain is a loop — the read
hits the loop-limit — a symlink-loop oracle.

## Oracle 10 — the `Not a directory`-names-the-prefix-miss

```
?file=/etc/passwd/x → "Not a directory" → ENOTDIR
```

`ENOTDIR` — a non-dir component in the path — the read tried, the
prefix isn't a dir — the path-structure oracle.

## Oracle 11 — the `I/O error`-names-the-io-fail

```
?file=/dev/sda → "I/O error" → EIO — the device-fail oracle
```

`EIO` — a device-read-failure — the file exists, the read failed at
the IO layer — a device-io oracle.

## Oracle 12 — the `Argument list too long`-names-the-args-limit

```
?file=<huge-path> → "Argument list too long" → E2BIG
```

`E2BIG` — the args-limit — the path is too long for the syscall —
a length-limit oracle.

## Oracle 13 — the `No space left`-names-the-write-fail

```
?file=/x → "No space left on device" → ENOSPC — the write-fail oracle
```

`ENOSPC` — the write-sink fails — the disk is full — a write-fail
oracle.

## Oracle 14 — the `Stale file handle`-names-the-nfs-miss

```
?file=/mnt/x → "Stale file handle" → ESTALE — the nfs-stale oracle
```

`ESTALE` — an NFS-handle stale — a network-fs oracle.

## Oracle 15 — the `Transport endpoint`-names-the-mount-fail

```
?file=/x → "Transport endpoint is not connected" → ENOTCONN
```

`ENOTCONN` — a fuse/network-mount disconnected — a mount-fail oracle.

## Oracle 16 — the `Structure needs cleaning`-names-the-fs-corrupt

```
?file=/x → "Structure needs cleaning" → EUCLEAN — the fs-corrupt oracle
```

`EUCLEAN` — a filesystem-corruption — a fs-state oracle.

## Oracle 17 — the `Read-only file system`-names-the-ro-mount

```
?file=/x → "Read-only file system" → EROFS — the ro-mount oracle
```

`EROFS` — the mount is read-only — a WRITE-fail oracle — read works —
`denied-conditions.md`.

## Oracle 18 — the `Exec format error`-names-the-format-miss

```
?file=/x → "Exec format error" → ENOEXEC — the exec-format oracle
```

`ENOEXEC` — a binary's format is wrong for the exec-sink — an exec-
format oracle.

## Oracle 19 — the `Invalid argument`-names-the-arg-miss

```
?file=%00 → "Invalid argument" → EINVAL — the arg oracle
```

`EINVAL` — a `%00`/bad-byte — the path-arg is invalid — the arg oracle.

## Oracle 20 — the `Interrupted system call`-names-the-signal

```
?file=/x → "Interrupted system call" → EINTR — the signal oracle
```

`EINTR` — a signal interrupted the read — rare.

## Oracle 21 — the `Bad file descriptor`-names-the-fd-miss

```
?file=/proc/self/fd/99 → "Bad file descriptor" → EBADF — the fd oracle
```

`EBADF` — an invalid fd — the `/proc/self/fd/99` oracle — the fd-number
oracle.

## Oracle 22 — the `Value too large`-names-the-size

```
?file=/x → "Value too large for defined data type" → EOVERFLOW
```

`EOVERFLOW` — a size/type overflow — a size oracle.

## Oracle 23 — the `Device or resource busy`-names-the-lock

```
?file=/x → "Device or resource busy" → EBUSY — the lock oracle
```

`EBUSY` — a locked-resource — a busy oracle.

## Oracle 24 — the `File exists`-names-the-collision

```
?file=/x → "File exists" → EEXIST — the collision oracle
```

`EEXIST` — an O_EXCL collision — a write-sink collision oracle.

## Oracle 25 — the `Too many open files`-names-the-fd-limit

```
?file=/x → "Too many open files" → EMFILE/ENFILE — the fd-limit oracle
```

`EMFILE`/`ENFILE` — the fd-table limit — a resource oracle.

## Oracle 26 — the `Cannot allocate memory`-names-the-oom

```
?file=/x → "Cannot allocate memory" → ENOMEM — the oom oracle
```

`ENOMEM` — an allocation-failure — a memory oracle.

## Oracle 27 — the `No such device`-names-the-device

```
?file=/dev/x → "No such device" → ENODEV — the device oracle
```

`ENODEV` — a device-path that doesn't exist — a device oracle.

## Oracle 28 — the `Not a tty`-names-the-tty

```
?file=/dev/x → "Not a tty" → ENOTTY — the tty oracle
```

`ENOTTY` — a non-tty device — a device-type oracle.

## Oracle 29 — the `Socket`-names-the-not-a-file

```
?file=/x → "Socket operation on non-socket" → ENOTSOCK
```

`ENOTSOCK` — a socket-op on a non-socket — a socket-type oracle.

## Oracle 30 — the `Operation not supported`-names-the-fs-cap

```
?file=/x → "Operation not supported" → EOPNOTSUPP/ENOTSUP
```

`EOPNOTSUPP`/`ENOTSUP` — the fs doesn't support the op — a cap oracle.

## The "the error is a fingerprint" — the fingerprint-map

The error-TYPE is the mechanism-map — `FileNotFound`/`Permission denied`/
`Is a directory`/`Too many levels`/`Not a directory`/`open_basedir`/
`disable_functions`/`allow_url_*` — the error names which layer
stopped it — the fingerprint-map is the oracle-driven corpus.
