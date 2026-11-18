# Apache Deep — handler mapping, MultiViews, and the upload-dir rules

## How Apache decides a file executes

```
request → location/directory match → type/handler resolution:
  mime.types maps ext→type (AddType)
  AddHandler maps ext→handler (php5-script, cgi-script, server-parsed)
  SetHandler forces ALL files in a context to a handler
  PHP-FPM: FilesMatch/SetHandler proxy:unix:...|fcgi://
```

The extension→handler map is the whole game — the upload exploit is either
an ext already mapped, or a config that makes one mapped.

## `AddHandler` / `AddType` / `SetHandler` — the semantic difference

- `AddType image/x-foo .foo` — declares a MIME type; does NOT execute
- `AddHandler php5-script .php` — declares the HANDLER (executes)
- `SetHandler application/x-httpd-php` — every file in scope → PHP
- `AddType application/x-httpd-php .php` — common config shorthand;
  mod_php reads the TYPE to exec — so `AddType ... .jpg` in `.htaccess`
  does the same as `AddHandler`

CTF `.htaccess` uploads try both:

```apache
AddType application/x-httpd-php .jpg
AddHandler php5-script .jpg
SetHandler application/x-httpd-php    # every file execs — heavy hammer
```

## MultiViews / mod_negotiation — the URL-less-extension trick

`Options +MultiViews`: `/uploads/shell` resolves `shell.php`/`shell.jpg`
by content negotiation — the extension isn't in the URL at all. Attack:

- upload `x.php` → fetch `/uploads/x` (no ext) → MultiViews picks it up
- helps when the ext whitelist stores `.jpg` but MultiViews finds `.php`?
  No — the FILE still needs the exec ext; it helps *reach* exec files whose
  URL path was blocked: fetch `/uploads/x%3f`? No — MultiViews is the
  variant-selection path.

Real MultiViews play: the app serves `x.jpg`, but `x.php` was also
uploaded — fetch `/uploads/x` and negotiation may serve `.php` over `.jpg`
if the client Accept prefers it.

## `mod_mime` extension walking — `x.php.xyz` execs

Apache walks extensions **right-to-left**, skipping unknown ones looking
for a recognized handler/type:

```
x.php.xyz  → .xyz unknown → .php → PHP handler → EXECUTES
x.php.aaa  → same
x.php.     → trailing dot → .php → executes
x.foo.php  → .php → executes (whitelist that reads first ext passes .foo!)
```

This is the canonical `.php.unknown-ext` bypass — the check reads last ext
(`.xyz` — whitelisted or unknown-and-allowed), Apache still runs PHP.

## `AddType` per-mime mapping files — `mime.types`

If you can overwrite `mime.types` (traversal) — `file-overwrite.md` —
add `application/x-httpd-php jpg`.

## `<FilesMatch>` / `Location` blocks — the exec scope

Apache configs often gate PHP to specific paths:

```apache
<FilesMatch "\.php$">SetHandler application/x-httpd-php</FilesMatch>
<LocationMatch "^/uploads/">Require all denied</LocationMatch>
<Directory /var/www/uploads>php_flag engine off</Directory>
```

If the upload dir has `php_flag engine off`, an `.htaccess` `php_flag
engine on` can REVERSE it (when AllowOverride covers Options/php.ini
directives — `AllowOverride Options` or `All` needed for `php_flag`).

## `AllowOverride` — what .htaccess can actually change

| AllowOverride | `.htaccess` can |
|---|---|
| `All` | everything incl. handlers |
| `FileInfo` | AddType/AddHandler/SetHandler — enough |
| `Options` | ExecCGI etc. |
| `Limit` | auth only |
| `None` | nothing — .htaccess dead |

Probe: upload `.htaccess` with `AddType` → fetch the file → if `.jpg` still
serves as image, `AllowOverride` doesn't cover it → try `.user.ini` next.

## `mod_rewrite`/`alias` — where the upload dir maps

`Alias /uploads /srv/data/uploads` — the URL path and filesystem path
decouple; the docroot rule (`php engine off` in a `<Directory>` on the
real path) decides exec.

## `suexec`/CGI — `Options +ExecCGI` path

```apache
Options +ExecCGI
AddHandler cgi-script .jpg
```

Then `x.jpg` with `#!/bin/sh\nid` + 0755 — runs as CGI. Shebang line +
exec bit matter — Apache honors the handler for the ext.

## Error-document/SSI angles — `server-parsed`

`AddHandler server-parsed .html` → `<!--#exec cmd="id"-->` in .html runs
SSI. `mod_include` — `Options +Includes` needed. `x.shtml`/`x.html` SSI
exec — rare but classic.

## php-fpm vs mod_php — which one matters

- mod_php: `.htaccess` `php_flag`/`php_value` apply; `AddType`/`AddHandler`
  map to the module
- php-fpm: `AddHandler` maps the ext to a proxy:fcgi handler;
  `php_flag`/`php_value` in `.htaccess` DO NOT work (they're mod_php
  directives) — use `.user.ini` instead; `SetHandler proxy:unix:/...` in
  `.htaccess` can't reach FPM — the per-dir `.user.ini` is the route

Detect: `X-Powered-By: PHP/x` + `Server` header alone doesn't split;
`SetHandler`/`proxy:fcgi` in the vhost config does; `.user.ini` works only
on FPM.

## The probe sequence for Apache uploads

```
1. is the dir inside docroot?  fetch /uploads/marker.txt → 200?
2. does php run there?         upload x.php → fetch → exec?
3. .htaccess accepted?         upload it → does a 500 fire? (500 = honored!)
4. AddType .jpg → fetch x.jpg → execs?
5. .user.ini → auto_prepend_file → fetch x.jpg
6. MultiViews → /uploads/x resolves x.php?
7. mod_mime walk → x.php.unknown → fetch → execs?
8. ExecCGI + cgi-script ext → runs shebang script?
```

A `500` on fetch after `.htaccess` upload is GOLD — Apache read the file
and hit a disallowed directive — meaning `AllowOverride` partially applies:
iterate directives until one sticks.

## Falsifiers

- uploads land outside the docroot or on a separate static vhost — no
  Apache-side exec exists at any config level
- `AllowOverride None` AND FPM `.user.ini` disabled (`user_ini.filename`
  custom) AND ext whitelist airtight AND mapping sane

## Output to record

- the directive that changed the mapping + the verbatim exec output
