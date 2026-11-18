# Execution Paths — how a stored file becomes code

## The point — "upload succeeded" is where exploitation starts

A `.php` file sitting in `/srv/uploads/` on a static vhost is inert.
Execution needs an interpreter to touch it. Enumerate the paths:

```
serve+exec     — upload dir inside a PHP/ASP/JSP-mapped docroot
include        — LFI/partial-include of the stored path
phar://        — metadata unserialize or include of phar stub
template       — file lands in a template dir → SSTI
config         — file lands as .htaccess/.user.ini/web.config
parser-exec    — ImageMagick/Ghostscript/LaTeX delegate runs it
import-exec    — importer evaluates (package install hooks, .pth, etc.)
argv           — filename reaches a command line
```

## Direct serve+exec — the simple case

Upload `x.php` → fetch `/uploads/x.php?c=id`. Works when the upload dir is
inside the PHP-FPM/mod_php docroot AND no config disables engine there.
Markers of the docroot: uploads served from the same origin, same scheme,
`.php` files elsewhere on the site execute.

Signals it's mapped-but-blocked: `.php` fetch returns 403 (not 404) —
forbidden-by-rule vs not-found. 403 = file IS there but a rule denies —
try `.pht`/`.phtml`/case variants, or the `x.php/x` nginx trick.

## Include — the stored file reaches a `require`/`include`

Any LFI/relative-path primitive pointing at the upload path:

```
?page=uploads/x.jpg&c=id        — PHP include executes the .jpg's <?php
?page=uploads/x.png%00           — legacy null-truncate
?page=phar://uploads/x.phar/inner — phar include
```

PHP include executes `<?php` blocks inside ANY bytes — the file does not
need a `.php` name or a clean structure; a GIF89a+PHP polyglot included
executes. Python/Node don't "include" files — this path is PHP-specific;
for other stacks the include-equivalent is template/import
(`framework-sinks.md`).

## phar:// — deserialization or include without exec perms

`phar://uploads/x.phar/inner.php` — works when the app calls any file-op
on a path you control (`file_exists`, `getimagesize`, `include`) and
`phar` wrapper is enabled (default on). Two wins:

- metadata `unserialize` → POP gadget → `../web-deserialization` skill
- `include 'phar://x/inner'` executes the inner file directly

The phar file needs no `.phar` ext — `phar://` reads the stream. Mint with
`tools/web/archive_gen.py phar --out x.phar --marker` (canary) or
`--metadata 'O:...'` (chain).

## Template overwrite — the file lands in a template dir

apexsurvive shape: an admin file-write + joined path drops content over
the template a route renders → SSTI on next render. Also: uploads into
`templates/`/`views/`/`themes/` dir directly.

```
upload → ../../templates/base.html   — Jinja2/Twig/Nunjucks payload in body
GET /route-that-renders-base          — SSTI fires
```

Caveat (the chain card's trap): template caches are per-worker — a worker
that already rendered the template won't reload it. Don't overwrite server
config to force reload — re-request the route until a cold worker serves
it.

## Config upload — change the rules

`.htaccess`/`.user.ini`/`web.config`/`mime.types`/`uwsgi.ini`/`supervisord`
→ `server-configs.md`. The file doesn't execute — it changes what executes.

## Parser-exec — the file is code to a converter

- ImageMagick MVG/MSL → `image-attacks.md`
- Ghostscript `.ps`/`.eps`/`.pdf` → `image-attacks.md`
- LaTeX `.tex` `\write18` → `document-attacks.md`
- Importer eval: `.pth` into site-packages, `setup.py`/`install.rb` in
  package archives, `plugins/`/`extensions/` dir uploads run at load

## Import-exec — files the app will RUN

- plugin/module upload endpoints (`/admin/plugins/install`) — a "plugin"
  zip contains code the app loads → RCE by design (htb-novacore shape:
  scanner sees archive, loader sees executable — polyglot between the two)
- theme/style uploads executed at render (CSS with `expression()` —
  legacy IE only, dead; template-partial themes → SSTI)
- `.crx`/`.xpi` extension installers — browser-side, bot-scope
- `Makefile`/`Dockerfile`/`package.json` scripts — CI/build pipes that
  run the uploaded manifest

## Argv — the filename reaches a shell

`htb-magicom` shape — `convert`/`identify`/`ffmpeg` called with the
filename interpolated:

```bash
# filename that becomes an argv option:
filename='x.png -write /tmp/o.png'
filename='x.png|id > /var/www/o.txt'
# ffmpeg concat/lavfi style:
filename='x.avi -vf "drawtext=textfile=/flag"'
```

Detect: error output echoing the filename inside a shell error
(`sh: 1: -write: not found`), or the command visible in logs/errors.
White-box: `exec(`, `shell_exec`, `subprocess`, `spawn(` with the
original filename.

## The "code reads the file" path — eval'd contents

The app `eval`s/`Function()`s/`exec()`s the uploaded content (import of a
"custom script" field) — no filesystem exec needed; the content IS the
payload.

## The "file served but never run" → pick the right pivot

| Served how | Pivot |
|---|---|
| verbatim text/plain | include it (PHP) or give up exec → other impacts |
| `Content-Disposition: attachment` | include/phar/template, not browser |
| different vhost, static only | include/phar; or impact-only (XSS if html) |
| inside object storage | SSRF-to-fetch or presigned-URL abuse — `cloud-storage.md` |
| never served | second-order — `second-order-processing.md` |

## Falsifiers

- the file is only ever stored — no serve, no include, no parser, no
  import, no argv
- every interpreter that could touch it is provably unreachable

## Output to record

- which execution path fired + the verbatim proof (executed output or
  rendered template)
- for include/phar: the controlling endpoint + the path argument
