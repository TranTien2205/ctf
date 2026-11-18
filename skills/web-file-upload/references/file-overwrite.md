# File Overwrite — when the write IS the payload

## The shape — no execution needed if the bytes land over something loaded

```
upload → path control (filename traversal, dir field, rename API)
      → overwrite an app file
      → next load/render/exec runs your bytes
```

The app overwrites itself; you never needed a shell.

## High-value overwrite targets — ranked by payoff

| Target | Effect | Notes |
|---|---|---|
| template file | SSTI → RCE | apexsurvive — overwrite the rendered template, request the route |
| `.htaccess`/`.user.ini`/`web.config` | handler remap → exec whitelisted ext | `server-configs.md` |
| `settings.py`/`config.php`/`.env` | config overwrite — keys, paths, debug | can break instance — read blast_radius |
| `__init__.py`/module file | code exec on next import | worker must reload — or it never fires |
| `requirements.txt`+CI hook | supply-chain on next build | slow |
| `authorized_keys`/`.ssh` | shell access | rarely writable as app user |
| `index.php`/`index.html` | front-door takeover | DirectoryIndex priority |
| `composer.json`/`package.json` + hook | exec on next install | CI-pipe only |
| `passwd`/`shadow` writable? | never — app isn't root | skip |
| `webroot/anything.php` | direct exec — trivial overwrite of an existing exec file | |

## The traversal into an overwrite — the mechanics

```
filename="../templates/base.html"               # relative into app dir
filename="/app/templates/base.html"             # absolute
{"path":"../templates/base.html"}               # dir/path fields
rename API: POST /rename {from:x, to:../t.html} # two-step sinks
```

Confirming which file landed: the write response echoes the stored path;
fetch the *template route* — the render output changes (marker text in
your overwrite shows in the response).

## The "must parse" validator — polyglot overwrite

apexsurvive shape: the file-write API requires the uploaded file to be a
valid PDF. The payload bytes go inside the PDF content stream so the file
parses as PDF AND carries the template-injection text that the renderer
will evaluate when the overwritten template is rendered. PDF is the
validator's requirement — the injected string is the engine's.

```
%PDF-1.4
1 0 obj << /Length 200 >> stream
{{7*7}}                                   ← payload visible to Jinja
endstream endobj
```

The rendered route's template engine evaluates `{{7*7}}` → `49` proves
SSTI → `web-ssti` for the full chain.

## Reload semantics — when does the overwrite fire

| Runtime | Fires when |
|---|---|
| PHP interpreted | every request — immediate |
| Jinja2/Django templates | per-worker template cache — new worker picks it up; old cached worker won't |
| Python modules | only on process restart — usually dead unless a reload hook |
| Node requires | only on restart — same |
| static file | every request — immediate |

Template-cache caveat (the card's trap): overwriting `base.html` then
hitting the route once may serve the OLD cached version from the worker
that had rendered it. The non-destructive fix is re-requesting — a worker
that has never rendered the route reads the file fresh. Overwriting a
server config to force a reload can brick the instance.

## Safe-targeting — what NOT to overwrite

Read `blast_radius` on the matching chain card first:

- server config / imported module — can permanently brick the instance
- DB files / migration state
- the upload handler itself (unless a restore path exists)
- another tenant's files (shared instance)

Prefer a target that renders on request (a template, a static include) —
the blast radius is one route's render, not the process.

## Detection — find writable targets

White-box grep:

```
move_uploaded_file.*\$name|copy.*filename|rename.*path|f.write|put_contents
```

Black-box: upload a marker file via traversal to a GUESSABLE target, fetch
the expected URL — a 200 with your marker proves the landing. Targets to
probe: `../static/m.txt`, `../templates/m.txt`, `../../app/m.txt`, `../m.txt`.

## Falsifiers

- the write root is jail-locked (`open_basedir`, `realpath` containment,
  chrooted worker) — traversal cannot leave it
- every candidate target is read-only to the app user
- no load/render ever touches an overwritable file

## Output to record

- the overwritten path + the payload carried
- the route that renders/loads it + verbatim proof it fired
- the reload mechanism used (or "fresh worker caught it")
