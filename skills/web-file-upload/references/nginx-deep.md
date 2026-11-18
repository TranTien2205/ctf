# Nginx Deep — location blocks, split_path, and alias tricks

## Why Nginx is different — no .htaccess

Nginx has no per-directory config files. All routing/exec decisions live in
the server config — you cannot upload config that changes behavior. The
attacks are instead **confusions in the existing config** — regex locations,
`alias` joins, `fastcgi_split_path_info`.

## `fastcgi_split_path_info` — the classic `.jpg/.php` exec

Typical misconfig:

```nginx
location ~ \.php$ {
    fastcgi_split_path_info ^(.+\.php)(/.+)$;
    fastcgi_pass unix:/run/php-fpm.sock;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}
```

`split_path_info` splits `/uploads/x.jpg/x.php` into script=`x.jpg` +
pathinfo=`/x.php` — FPM executes `x.jpg` as PHP. Upload `x.jpg` = a PHP
polyglot, fetch `/uploads/x.jpg/x.php` → executes.

Variants to probe:

```
/uploads/x.jpg/x.php          # standard
/uploads/x.jpg/.php           # dot-only pathinfo
/uploads/x.jpg%00.php         # NUL-truncate (old PHP-FPM)
/uploads/x.jpg%2f..%2f..%2f.php  # encoded split
/uploads/x.php/../x.jpg       # pathinfo normalization
```

Detection: fetch `/uploads/<any-real-file>.jpg/x.php` — a PHP-processed
response (200 with php output, or a PHP-specific error/`X-Powered-By:
PHP` header, `File not found.` from FPM) means the split is on. A static
`404` (nginx-generated HTML error page) means it's off.

## `alias`/`root` confusion — path escapes via URL

```nginx
location /uploads {
    alias /srv/data/uploads/;      # trailing slash matters!
}
```

`/uploads../x` — location matches `/uploads` prefix, alias appends
`../x` → `/srv/data/uploads/../x` = `/srv/data/x` — directory escape.
Probe `/uploads../` for parent-dir leaks.

```nginx
location /uploads/ {
    root /srv/data;
}
```

`/uploads/../x` normalizes to `/x` under `root`? nginx normalizes `..`
before location matching — `merge_slashes`/`merge_slashes off` variants.

## `merge_slashes` — `//` location mismatch

`merge_slashes off` + regex `~ \.php$` — `//uploads//x.php` may bypass a
`location ^~ /uploads/` static rule while still matching `\.php$` →
exec where static was intended, or vice versa.

## `try_files` and named locations — second-chance processing

```nginx
location / { try_files $uri $uri/ @php; }
location @php { fastcgi_pass ...; }
```

`/uploads/x.jpg/nonexistent` → try_files falls to @php → FPM gets the URI —
execs `x.jpg` as PHP? Depends on SCRIPT_FILENAME — probe.

## `location ~ \.php$` vs prefix `location /uploads/` — which wins

Regex locations beat prefix locations (except `^~` prefix). A `/uploads`
dir where the admin expected "static only" — but `~ \.php$` regex still
matches `x.php` inside it → exec despite a "static" prefix block. Probe:
upload `.php`, fetch → executed = the regex is loose.

## `internal` locations — files served only internally

`location /internal/ { internal; }` — direct fetch 404s; but `X-Accel-
Redirect` from the app may serve it — the upload lands there and an app
endpoint (`download.php?f=`) emits `X-Accel-Redirect: /internal/x` —
the fetch goes through the app's redirector. Check `X-Accel-Redirect` on
download endpoints.

## The `static + fpm` split — uploads on a separate server

```
server { listen 80; server_name static.x; location / { root /srv/s; } }
server { listen 80; server_name app.x; location ~ \.php$ { fpm } }
```

`x.php` uploaded to `static.x` never execs — same filesystem, different
vhost. The route is then include/`phar://`/`X-Accel-Redirect`, or finding
a path on `app.x` that serves the same dir.

## `limit_except`/`dav` methods — PUT uploads

`dav_methods PUT` on the upload location → `PUT /uploads/x.php` direct —
bypass the app's upload endpoint entirely. Probe `PUT` directly.

## `.user.ini` doesn't work — nginx has no per-dir php.ini

`.user.ini` is a PHP-FPM feature independent of the web server — it DOES
work under nginx+php-fpm (it keys on the script's directory, not the
server). `apache-deep` vs this: `.htaccess` = Apache-only; `.user.ini` =
FPM-anywhere.

## The `cgi.fix_pathinfo=1` story — the root cause

The `.jpg/.php` trick only works because `cgi.fix_pathinfo=1` (default)
tells FPM to walk back to the nearest existing file. `=0` kills it. On a
hardened config it fails — confirm the split exists before iterating.

## Probe sequence

```
1. fetch /uploads/m.txt                → dir served?
2. fetch /uploads/x.php               → exec or 403/404?
3. fetch /uploads/x.jpg/x.php         → split_path exec?
4. fetch /uploads../                  → alias escape?
5. upload .user.ini + x.jpg           → auto_prepend_file fires?
6. PUT /uploads/x.php                 → dav_methods on?
7. download endpoint → X-Accel-Redirect → internal path?
```

## Falsifiers

- every location returns static (no regex/fpm reach to the upload dir)
- `cgi.fix_pathinfo=0` + no `alias` confusion + no internal redirect path

## Output to record

- the config weakness proven + the verbatim exec output
