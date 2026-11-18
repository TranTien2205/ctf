# Denied Conditions — when the read class is dead

## The absolute kill — `verdict=refutes`

- absolute-path probe → `Access denied`/`No such file`/`Entity not
  defined`-equivalent + the file DOES exist → the mechanism is dead
- every rung of the traversal ladder → no content + no error → the
  param doesn't reach the filesystem

## The `open_basedir` wall — PHP confine

```
Warning: open_basedir restriction in effect.
  File(/etc/passwd) is not within the allowed path(s):
  (/var/www/html:/tmp)
```

`open_basedir` — the PHP confine — `file:///`/`php://`/`include` all
respect it — the confine is the kill for that surface. `../../proc/self/root/`
may escape it on some configs — the chroot-escape is the exception.

## The `disable_functions` wall — PHP exec-kill

```
Warning: include() has been disabled for security reasons
```

`disable_functions=include,require,include_once,require_once,eval,
system,exec,shell_exec,passthru,popen,proc_open,pcntl_exec` — the
exec-kill — a `file_get_contents` read survives, an `include` dies.

## The `allow_url_include`/`allow_url_fopen` wall — PHP remote-kill

`allow_url_include=Off` → `include 'http://...'`/`include 'php://input'`/
`include 'data://...'` all die — `allow_url_fopen=Off` → `file:///`/
`php://`/`http://`/`ftp://`/`data:`/`phar://`/`zip://`/`glob://`/
`expect://`/`ssh2.*`/`rar://`/`ogg://` all die — the remote-wrapper kill.

## The `realpath`-confine — the non-PHP wall

```python
base = "/var/www/files"
path = os.path.realpath(os.path.join(base, user_input))
if not path.startswith(base): raise
```

`realpath`-confine — the absolute-path-then-prefix-check — `../`/
absolute-path/`..`-normalize all resolve → `startswith` fails → the
confine is real — the kill for the traversal-ladder on that surface.

## The `realpath`-escape — the `/proc/self/root` edge

`realpath` resolves symlinks — `/proc/self/root/` = `/` — `realpath
('/app/../../proc/self/root/etc/passwd')` = `/etc/passwd` — the
`startswith('/app')` check fails BUT the traversal worked — wait no
— `realpath` returns `/etc/passwd` not `/app/../...` — the confine
DOESN'T hold if `realpath` is the check — actually it DOES — the
escape is `/proc/self/root/` INSIDE the realpath — `startswith` on
`/etc/passwd` fails — the confine holds UNLESS `realpath` isn't the
confine-check — the `realpath`-confine is REAL when the check is
`realpath(...).startswith(base)` — the `/proc/self/root` edge needs
a different confine (a chroot) to bypass.

## The `chroot`/`jail` wall — the container-confine

`chroot /app` — the fs-root is `/app` — `/etc/passwd` = `/app/etc/passwd`
— the traversal lands in the jail — `/proc/self/root/` escapes if
`/proc` is mounted inside the jail AND `chroot` isn't the container's
own mount-ns.

## The `send_from_directory`/`safe_join` wall — the Flask-style

`send_from_directory('/files', name)` — werkzeug's `safe_join` — the
confine is enforced — traversal fails — `windows`-edge: `safe_join` +
`..`+`/` on Windows → drive-relative escapes historically — `per-stack.md`.

## The `path.join`+`resolve`+`startsWith` — the Node-style

`path.resolve(base, user).startsWith(base)` — the resolved-prefix —
`..` resolves out — the confine holds — unless `path.join` vs `resolve`
subtlety.

## The `Path.resolve`+`is_relative_to` — the Python-3.9-style

`Path.resolve(base, user).is_relative_to(base)` — the modern confine —
the kill for `..`-traversal on that surface.

## The `VirtualPathProvider`/`MapPath` wall — the .NET-style

`MapPath("~/x")` maps `~` to the webroot — `~/../../` fails — the
virtual-path confine — `per-stack.md`.

## The `SecurityManager`/`AccessController` wall — the Java-style

`System.getSecurityManager().checkRead(path)` — the Java security-
policy confine — `doPrivileged` blocks it — rare in CTF.

## The `getResourceAsStream` classpath wall — the Java-archive confine

`getResourceAsStream("/x")` resolves inside the JAR — `..` doesn't
escape — `file:///` absolute still works through `FileInputStream` —
the classpath-confine is jar-internal.

## The `SELinux`/`AppArmor`/`seccomp` wall — the LSM-confine

`/proc/self/attr/current` reveals the LSM context — `type=...` —
an LSM may confine file-reads regardless of the app's check — the
kill is at the kernel layer — `denied` errors in `dmesg`/`audit.log`.

## The `fsnotify`/`fanotify`/`audit` wall — the monitor-confine

An `auditd`/`fanotify` watcher — the read still works but is LOGGED —
the read isn't denied, it's logged — a detection-risk, not a block.

## The `read-only-fs`/`mount --bind --read-only` wall — the mount-confine

`/proc/self/mounts` reveals `ro`/`bind` mounts — a read-only mount —
the read works, the write fails — a write-kill not a read-kill.

## The `immutable`/`chattr +i` wall — the file-attr confine

`chattr +i /flag` — the file is immutable — READ works, write fails —
a write-kill.

## The `capabilities`/`DAC`/`posix` wall — the perm-confine

`/proc/self/status` `Uid:`/`Gid:` — the app runs as `www-data` —
`/root/*`/`/etc/shadow` fail with `Permission denied` — the perm-confine
— the flag may be `chmod 400` — the read can't reach it — try a
setuid-binary or the `/proc/1/root` escape.

## The `encryption`-at-rest wall — the dm-crypt confine

`dm-crypt`/`LUKS` — the flag file's block-device is encrypted — the
mounted view is decrypted — `mountinfo` reveals — the read gets the
decrypted content normally — a non-issue usually.

## The "the read is confined AND the flag is outside" — the honest note

`/app` confine + flag at `/flag` — the confine kills the read — unless
`/proc/self/root`/`mountinfo`-reveals-a-mount/symlink escapes — the
kill-map records which escapes were tried.
