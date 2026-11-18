# Include vs Read — the RCE boundary

## The critical distinction — `include`/`require` executes

A `include 'file.php'` EXECUTES the file's PHP — a `file_get_contents`
doesn't. The same `?file=` param means completely different things
depending on which sink it feeds:

| Sink | The primitive |
|---|---|
| `include`/`require`/`include_once`/`require_once` | RCE — code runs |
| `file_get_contents`/`readfile`/`file`/`fpassthru`/`readgzfile`/`show_source`/`highlight_file` | read-only |
| `include` + `php://filter` | read — filter makes it not-code |
| `include` + `php://input`/`data:` | RCE — body/data executes |

## The `include`-as-read trick — `php://filter` in an `include`

```php
include "php://filter/convert.base64-encode/resource=config.php";
```

`include` on a filter-wrapped path — the base64 stream isn't PHP code —
it's a READ, not execution — the source is base64'd into the output —
the source-read-through-an-include-sink.

## The `include`-as-RCE — the body/data trick

```php
include "php://input";                          — request body executes
include "data://text/plain;base64,<b64-php>";   — data: executes
include "expect://id";                          — expect executes
include "/tmp/x.php";                           — the file's PHP executes
include "/var/log/apache2/access.log";          — log-injection → RCE
```

The `include` sink + a stream-wrapper with code = RCE — `read-to-rce.md`.

## The `readfile`/`file_get_contents`/`file`/`fpassthru`/`show_source`/`highlight_file`/`readgzfile`/`parse_ini_file`/`md5_file`/`hash_file`/`filectime`/`filemtime`/`fileatime`/`filesize`/`file_exists`/`is_file`/`is_readable`/`is_dir`/`is_link`/`stat`/`lstat`/`realpath`/`pathinfo`/`basename`/`dirname`/`readline`/`get_meta_tags`/`mime_content_type`/`filetype`/`fileperms`/`finfo_file`/`exif_read_data`/`getimagesize`/`imagecreatefrom*`/`xxhash_file`/`SplFileObject`/`RecursiveDirectoryIterator`/`DirectoryIterator`/`FilesystemIterator`/`glob`/`scandir`/`opendir`/`readdir` — the READ family

The big list of read-family functions — each takes a file/path/stream —
the same wrappers apply — `php://filter`/`phar://`/`zip://`/`glob://` —
`include`/`require` are the ONLY exec-sinks.

## The `unlink`/`rename`/`copy`/`mkdir`/`rmdir`/`touch`/`chmod`/`chown`/`symlink`/`link`/`move_uploaded_file`/`file_put_contents`/`fwrite`/`fputs` — the WRITE family

The write-family — a `phar://`/`zip://` trigger through `unlink`/`stat`
/`copy` — `file_put_contents` writes — the LFI-to-write edge.

## The `opendir`/`scandir`/`glob`/`readdir` — the listing family

```php
glob("/var/www/html/*.php")      — the listing read
scandir("/etc/")                  — the dir contents
opendir("/etc/")                  — the dir handle
```

The directory-listing oracle — `glob://*` reads the dir contents —
`glob`/`scandir` return a LIST not file-content — a different primitive
shape.

## The "the sink is a function that happens to take a path" — the side-channel sinks

```php
$finfo = finfo_open(FILEINFO_MIME_TYPE);
finfo_file($finfo, "/etc/passwd")       — reads the file → returns mime-type
mime_content_type("/etc/passwd")
filesize("/etc/passwd")                  — the size-oracle
file_exists("/etc/passwd")               — the existence-oracle
is_readable("/etc/passwd")
is_writable("/etc/passwd")
is_dir("/etc/")
realpath("/etc/passwd")
filetype("/etc/passwd")
fileatime("/etc/passwd")                 — the atime-oracle
exif_read_data("/etc/passwd")            — the exif-parse
getimagesize("/etc/passwd")              — the image-parse
md5_file("/etc/passwd")                  — the md5-oracle — content-hash!
sha1_file("/etc/passwd")
hash_file("md5", "/etc/passwd")
```

`md5_file`/`sha1_file` — a content-hash oracle — the file's MD5 is
leaked — compare against known hashes — the "is this file X" oracle
without reading.

## The "the sink is a partial-read" — the header/magic read

`finfo_file`/`mime_content_type`/`exif_read_data`/`getimagesize` —
parse the file's structure — a partial-read oracle — the "what kind
of file" and the metadata — a `getimagesize` on a PHP file errors —
the error reveals the file ISN'T an image — the type-oracle.

## The "the sink needs a writable path" — the write-sinks

```php
file_put_contents("/tmp/x.php", "<?php ...")
move_uploaded_file($tmp, "/app/uploads/x.php")
copy("/src", "/dst")
rename("/src", "/dst")
```

The write-sinks — `file_put_contents` + `php://filter` writes base64-
decoded content — `php://filter/convert.base64-decode/resource=x.php`
as the WRITE-path — the LFI-to-write chain — `read-to-rce.md`.

## The "the sink is `eval`/`assert`/`create_function`/`preg_replace-e`/`call_user_func`/`usort`/`array_map`/`array_filter`/`register_shutdown_function`/`register_tick_function`/`forward_static_call`/`ob_start`-with-callback — the eval-family

The eval-family — `eval($file_content)`/`assert`/`call_user_func` —
the file's CONTENT is executed — an LFI that feeds eval = RCE — the
eval-sink is the exec-sink.

## The "the sink is `unserialize`/`yaml_parse`/`json_decode`/`simplexml_load_string`/`DOMDocument`/`xml_parse`/`igbinary_unserialize`/`msgpack_unserialize`/`wddx_deserialize` — the deser-family

The deser-family — `unserialize($file_content)` — the file's content is
deserialized — `phar://`/`zip://`/`data://` feed it — the deser-sink —
`web-deserialization`.
