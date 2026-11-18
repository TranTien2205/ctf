# Common Mistakes — the budget-burning traps

## Iterating extensions before naming the layer

`shell.php3`, `.php4`, `.php5`, `.phtml`, `.PhP`... — twenty variants
against a content check that doesn't care about the extension. The
rejected-ext probe answers *which layer* speaks; iterate only within that
layer's family.

## Upload-success = exploit-success

`{"ok":true}` on the POST means storage. Fetch the file and grade the
serve: `served-raw`/`executed-or-transformed`/`blocked`/`gone` — via
`upload_probe.py verify`. The exploit question is never "did it accept"
but "does it execute or land over something".

## Fighting a whitelist it can't beat

Whitelist that checks the real stored name + mapping airtight + no config
upload → the extension game is over. Pivot: consumer-side
(`second-order-processing.md`), traversal (`path-traversal.md`), config
(`server-configs.md`), or parser-splits (`parser-differentials.md`).

## Missing the second endpoint

`/upload/avatar` is strict; `/import`, `/api/v2/files`,
`/admin/theme/install`, `/api/upload-url` (presigned) are not. The
inventory step isn't optional — `detection.md`.

## Testing `.php` on a Node stack

The stack tells you which extension family matters. `x.php` on Express is
meaningless — Node never executes by extension; the attack is always
content/parser/path there. Read the stack headers + page tech first.

## Polyglot in the wrong direction

Payload in a JPEG comment gets stripped on re-encode — `cmp` the fetched
bytes first. Payload in pixels survives GD-resize only under narrow
conditions — measure before crafting.

## Missing that the file is a CONSUMER target

The upload is for an importer/thumbnailer/converter — no serve path will
ever exist, and extension gymnastics are pure waste. Look for "what reads
this file later" the moment a marker upload isn't fetchable.

## `.htaccess` uploaded but Apache `AllowOverride None`

Config uploads need the server to honor them — `.htaccess` needs
`AllowOverride`, `.user.ini` needs PHP-FPM per-dir config, `web.config`
needs unlocked `handlers`/`staticContent`. Probe the fetch of the config-
file upload itself; a served `.htaccess` as text proves nothing until
Apache honors it.

## Serving-domain blindness

File served `image/svg+xml` but on a cookieless static domain — the XSS
works but steals nothing. Check the serve origin + cookies scope before
counting stored-XSS as a chain link.

## Filename ≠ stored name — reading the response wrong

The response may echo the *client* filename while storing a uuid — the
fetch path uses the stored name. Record both and always fetch the stored
one.

## Extension check on a param the store ignores

`filename="x.jpg"` checked while the file lands under `path=../../x.php`
from a sibling field — the check passed, the traversal won anyway.
Enumerate sibling fields before concluding the layer is beaten.

## Race-condition claims without a baseline

A 200-once hit on the fetch is not a race — it could be a slow-normal path.
`race_probe.py` with a serial baseline: a signature that appears serially
is not a race.

## Forgetting the `.` prefix on dotfiles

`.htaccess` and `.user.ini` are names without extensions — a naive split
on `.` yields `htaccess`-as-name or empty ext; a `*.*` whitelist passes
them, a blacklist on basename misses them. Try `filename=".htaccess"`.

## Claiming RCE from an `phpinfo()` echo — stopped too early

`phpinfo()` output proves exec — keep going to read the flag / chain the
impact; don't stop at the info page. But record it honestly: it's impact
proven, not the end state.

## Falsifier checklist — before declaring the class closed

- every upload endpoint probed (not just the obvious one)?
- every layer probed (ext, MIME, content, path, archive, consumer)?
- execution paths exhausted (serve+exec, include, phar, template, config,
  parser, argv)?
- the class falsifier confirmed (no retrieval + no consumer)?

## Output to record

- which trap was hit + what corrected the course
