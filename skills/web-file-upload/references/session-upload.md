# Session-File Upload — upload into PHP session storage

## The shape — PHP sessions are files; an upload can write one

`session.save_path` (default `/var/lib/php/sessions/` or `/tmp/`) stores
`sess_<id>` files containing serialized session data. An upload that
lands `sess_<id>` into the session dir — or an upload that SESSION data
gets read from — is the primitive.

## The classic chain — LFI + session-upload

```
1. `?page=php://filter/read=convert.base64-encode/resource=sess_<id>`
   reads your own session file — LFI via session file
2. store a `<?php` payload in a session var (via an upload form that
   saves a field into `$_SESSION`)
3. LFI `include` the session file → the serialized blob contains your
   `<?php` — PHP includes it as code → RCE
```

The session file's serialized format wraps your payload; `include`
evaluates the whole file including the serialized-text — the `<?php`
inside it executes.

## The `sess_<id>` filename — predictable?

`session_id()` is the cookie `PHPSESSID` — you control it partially
(`session_id(yourchoice)` if the app doesn't regenerate) — the filename
`sess_yourchoice` is predictable if you can set your session id.

## Session-upload progress tracking — PHP 5.4+ `session.upload_progress`

`session.upload_progress.enabled` — when a multipart POST includes
`PHP_SESSION_UPLOAD_PROGRESS`, PHP writes progress info into the
session file — the session file contains your submitted value:

```
POST /index.php
Content-Type: multipart/form-data

PHP_SESSION_UPLOAD_PROGRESS=<payload>
file=<anything>
```

The session file gets `upload_progress_123` keys containing your string —
if a field you control lands in the session file AND you can LFI/include
it — exec. This is the documented `session.upload_progress` chain — no
session-write needed, just a multipart POST.

## The "session file as include target" — the wrapper path

```
include '/var/lib/php/sessions/sess_' . $_COOKIE['PHPSESSID'];
```

OR `session.save_path` traversal — if the app reads
`session.save_path`/`session_id` from input — path control on the
session file itself.

## Detection — does the app put uploaded content into `$_SESSION`?

- a form field stored into `$_SESSION` (white-box: `$_SESSION['x'] =
  $_POST/FILES`)
- a `PHP_SESSION_UPLOAD_PROGRESS` field in the multipart
- the session file path is known/default
- an include/LFI primitive exists elsewhere

## The chain's full links — needs BOTH

```
upload/POST controls a value in the session file
        +
include/LFI reaches the session file path
        =
session content executes as php
```

Each link alone is a separate bug — the chain needs both.

## The "session data is already yours" case — user-controlled session

If the app stores user data in `$_SESSION` and you can put `<?php` in
that data — the session file contains it — the include is the only
missing link.

## Falsifiers

- no session file reachable by any include/read primitive
- no path lets attacker data reach the session file

## Output to record

- the session-file path + the field that reaches it + the include
  primitive that reads it
