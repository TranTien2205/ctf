# Blind File Read — oracles when the content never echoes

## The blind-read problem

The read happens — the content doesn't echo. The channel is timing,
errors, OOB, or a side-effect.

## Oracle 1 — `file_exists`/`filesize` — the existence-channel

```
?file=/etc/passwd       → 200 + "file exists"
?file=/nonexistent      → 404 + "not found"
```

`file_exists`/`filesize`/`filetype`/`is_readable` — the metadata oracle —
a file exists at the path the param names — a positive/negative match
= existence-leak.

## Oracle 2 — `md5_file`/`sha1_file`/`hash_file` — the hash-channel

```
?file=/etc/passwd       → md5 of the file
?file=/nonexistent      → error / empty
```

`md5_file`/`sha1_file`/`hash_file` — returns the file's HASH — the hash
of a KNOWN file (`/etc/passwd`, `/etc/hostname`) proves the read path —
the hash of an UNKNOWN file is a fingerprint — a content-hash oracle
not a content-read.

## Oracle 3 — `getimagesize`/`exif_read_data` — the image-meta channel

```
?file=/tmp/pic.jpg      → {"width":..., "height":..., "mime":...}
?file=/etc/passwd       → not an image → error/false
```

`getimagesize`/`exif_read_data`/`iptcparse`/`finfo_file` — the image-
metadata oracle — an image-shaped file returns its dimensions/mime —
a non-image returns error — an image-file-existence + mime oracle.

## Oracle 4 — `finfo_file`/`mime_content_type` — the mime-channel

```
?file=/etc/passwd       → text/plain
?file=/tmp/x.png        → image/png
?file=/nonexistent      → error
```

`finfo_file`/`mime_content_type` — returns the file's MIME — a mime-
type oracle — distinguishes text/binary/image/archive.

## Oracle 5 — the `include`-error-channel

```
?file=/etc/passwd       → include fails → parse error / warning
?file=/etc/hostname     → same
?file=/nonexistent      → file-not-found error — DIFFERENT error
```

`include` of a non-PHP file → `Failed opening`/`Parse error` — the
ERROR TEXT differs: `File not found` vs `Parse error in file` vs
`include(): Failed opening` — the error-TYPE is the oracle.

## Oracle 6 — the `readfile`-to-time channel — the size-timing

```
?file=/dev/zero         → hangs / very slow
?file=/dev/urandom      → hangs / entropy-read
?file=/etc/passwd       → fast
?file=/nonexistent      → instant error
```

A `readfile`/`fpassthru` that streams the content — `/dev/zero`/
`/dev/urandom` hang — timing reveals the read attempt — the size/
blocking oracle.

## Oracle 7 — the `/proc/self/fd/*` fd-oracle

```
?file=/proc/self/fd/3   → content of fd 3 — a socket/temp/pipe
?file=/proc/self/fd/99  → invalid fd → error
```

Reading `/proc/self/fd/N` — an fd the app already has open — the fd
number is the oracle — fd 3-30 typically.

## Oracle 8 — the `stat`/`fileatime`/`filemtime`/`filectime` channel

```
?file=/etc/passwd       → mtime=1234567890
?file=/nonexistent      → error
```

`filemtime`/`fileatime`/`filectime`/`fileatime`/`filesize` — the stat-
family — a file's timestamp/size is a metadata oracle.

## Oracle 9 — the `XML`-error channel — the XXE-adjacent

An `include`/`simplexml_load_file`/`dom`/`xpath`/`sax` — an XML-file
that's malformed → a parse-error names the file's line-number/content —
the XML-parse-error oracle — `web-xxe` adjacent.

## Oracle 10 — the `exif`/`iptc`/`id3`/`xmp` metadata channel

`exif_read_data`/`iptcparse`/`id3_get_tag`/`xml_parse` on media —
the metadata returns tag-values — a media-file-metadata oracle.

## Oracle 11 — the `archive`-list channel

`zip://`/`rar://`/`phar://`/`tar` — the archive-member listing — the
archive's internal structure leaks — `zip://x.zip#`+member — a listing
oracle inside an archive.

## Oracle 12 — the `glob`/`scandir`/`opendir`/`dir`/`readdir` listing

```
glob:///*
scandir('/etc/')
opendir('/etc/') + readdir()
```

The listing-family — returns a directory LISTING — a weaker primitive
than a file-read but still leaks the filesystem layout.

## Oracle 13 — the `file`/`filegroup`/`fileowner`/`fileperms`/`fileinode`/`fileatime`/`filectime`/`filemtime`/`filesize`/`filetype` stat-family

The full `stat` family — every metadata field — the "the file exists
with these attrs" oracle.

## Oracle 14 — the `is_file`/`is_dir`/`is_link`/`is_readable`/`is_writable`/`is_executable`/`is_uploaded_file`/`is_link`/`realpath` family

The `is_*`/`realpath` family — the path-type oracle — a symlink's
target leaks via `readlink`/`realpath`.

## Oracle 15 — the `dirname`/`basename`/`pathinfo`/`realpath` path-family

`realpath`/`dirname`/`basename`/`pathinfo` — returns the resolved path —
a path-normalization oracle — reveals the actual filesystem layout.

## Oracle 16 — the `tempnam`/`tmpfile`/`sys_get_temp_dir`/`memory`/`temp`/`stream_get_meta_data`/`stream_is_local`/`stream_isatty`/`stream_supports_lock`/`stream_wrapper_register`/`stream_wrapper_restore`/`stream_wrapper_unregister`/`stream_context_create`/`stream_context_get_default`/`stream_context_get_options`/`stream_context_set_default`/`stream_context_set_option`/`stream_context_set_params`/`stream_copy_to_stream`/`stream_encoding`/`stream_filter_append`/`stream_filter_prepend`/`stream_filter_register`/`stream_filter_remove`/`stream_get_contents`/`stream_get_filters`/`stream_get_line`/`stream_get_meta_data`/`stream_get_transports`/`stream_get_wrappers`/`stream_is_local`/`stream_isatty`/`stream_resolve_include_path`/`stream_set_blocking`/`stream_set_chunk_size`/`stream_set_read_buffer`/`stream_set_timeout`/`stream_set_write_buffer`/`stream_socket_accept`/`stream_socket_client`/`stream_socket_enable_crypto`/`stream_socket_get_name`/`stream_socket_pair`/`stream_socket_recvfrom`/`stream_socket_sendto`/`stream_socket_server`/`stream_socket_shutdown`/`stream_supports_lock`/`stream_wrapper_register`/`stream_wrapper_restore`/`stream_wrapper_unregister` family

The `stream_*` family — PHP's stream API — a `stream_get_meta_data`
oracle — a `stream_is_local` — a `stream_get_wrappers` — the stream-
surface oracle.

## Oracle 17 — the `SplFileInfo`/`SplFileObject`/`SplTempFileObject`/`SplFixedArray`/`DirectoryIterator`/`FilesystemIterator`/`GlobIterator`/`RecursiveDirectoryIterator`/`RecursiveIteratorIterator`/`RecursiveTreeIterator`/`SplFileObject`/`SplTempFileObject`/`SplObjectStorage`/`SplPriorityQueue`/`SplQueue`/`SplStack`/`SplDoublyLinkedList`/`SplMinHeap`/`SplMaxHeap`/`SplHeap`/`SplFixedArray`/`SplObserver`/`SplSubject`/`SplFileInfo`/`SplFileObject`/`SplTempFileObject`/`SplFixedArray`/`SplDoublyLinkedList`/`SplStack`/`SplQueue`/`SplHeap`/`SplMaxHeap`/`SplMinHeap`/`SplPriorityQueue`/`SplObjectStorage`/`SplObserver`/`SplSubject`/`ArrayIterator`/`ArrayObject`/`AppendIterator`/`CachingIterator`/`CallbackFilterIterator`/`Countable`/`DirectoryIterator`/`EmptyIterator`/`FilesystemIterator`/`FilterIterator`/`GlobIterator`/`InfiniteIterator`/`Iterator`/`IteratorAggregate`/`IteratorIterator`/`LimitIterator`/`MultipleIterator`/`NoRewindIterator`/`OuterIterator`/`ParentIterator`/`RecursiveArrayIterator`/`RecursiveCachingIterator`/`RecursiveCallbackFilterIterator`/`RecursiveDirectoryIterator`/`RecursiveFilterIterator`/`RecursiveIterator`/`RecursiveIteratorIterator`/`RecursiveRegexIterator`/`RecursiveTreeIterator`/`RegexIterator`/`SeekableIterator`/`Serializable`/`SplFileInfo`/`SplFileObject`/`SplTempFileObject` family

PHP's SPL — `SplFileObject`/`DirectoryIterator`/`GlobIterator` — the
SPL file-surface — a `SplFileObject->fgets()` — an SPL-read primitive.

## Oracle 18 — the `phar`/`Phar`/`PharData`/`PharFileInfo`/`PharException`/`Phar::*` family

`new Phar('/x.phar')`/`Phar::loadPhar`/`PharData` — the phar-surface —
a `Phar` object's `getMetadata()`/`offsetGet()` — the phar-meta oracle.

## The "the read is blind, chain to OOB" — `oob`-family

An include/exec-sink → `php://input`+`curl`/`wget`/`mail` — the OOB
channel — `oob_listener` capture — the blind-read→OOB-exec chain.

## The "the read is blind, record surface-level" — the honest note

A blind read with no channel — record `verdict=inconclusive`/`surface` —
the blind-read is weaker than a content-read — don't claim content
you didn't see.
