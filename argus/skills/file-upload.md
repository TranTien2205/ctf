# File upload

**When:** any upload input. The two questions: (1) can you store a file the
server will execute or serve dangerously? (2) where is it served from?

## Map the checks first

Upload a benign canary (`argus<rand>.txt`, content `argus<rand>`) and find
where it lands: response body, predictable path (`/uploads/<name>`),
`/files/<id>`, Content-Disposition, or an internal id. You cannot exploit an
upload you cannot reach afterward.

## Bypass matrix - change ONE thing at a time

| Check | Bypasses |
|---|---|
| Extension blacklist | `.php5`, `.phtml`, `.phar`, `.pht`, `.asp`, `.aspx`, `.jsp`, case `PhP` |
| Extension whitelist | double ext `x.php.jpg`, null byte `x.php%00.jpg`, trailing dot/space, `x.jpg;.php` (IIS) |
| Content-Type sniff | keep valid image bytes + appended payload; polyglot GIF `GIF89a;` header |
| MIME header check | send `image/png` with .php body - many apps trust the header alone |
| Image re-render | payload in EXIF/metadata or after IEND survives naive re-encoding |
| Path in filename | `../../x.php` as filename -> traversal on save |
| .htaccess/web.config upload | make the server execute `.jpg` as PHP/ASP in that dir |

## Execute, then clean up

Fetch the uploaded file. A `.php` returning your marker (`<?php echo 'ARG';?>`)
proves server-side execution - that alone is the finding; `id`-level output
is enough, never webshell on a real engagement. SVG with script content =
stored XSS alternative when code exec fails. Then DELETE the artifact when
the API allows.

## Secondary sinks worth one probe each

- Archive extraction (`zip`, `tar`) -> slip `../../` entries
- ImageMagick/ffmpeg processing -> known CVE classes, filename injection
- XML upload -> XXE (see `xxe` skill)
- CSV -> formula injection `=cmd|...` (downstream Excel, medium-low)

## Falsifier

Executable extensions rejected AND re-encoding strips payloads AND stored
files land outside web root or force-download with safe types.

## Severity guide

Server-side code execution: critical. Stored XSS via upload: medium-high.
Traversal write outside web root: high. Upload accepted but unreachable/
inert: low-info.
