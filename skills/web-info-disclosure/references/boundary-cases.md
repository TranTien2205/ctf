# Boundary cases — where the canonical recipe bends

## The catch-all that diffs by content

A dynamic catch-all embeds the requested path in the body — byte-diff lies.
Compare on the structural fingerprint (same template, same scripts, same
length range), not on byte equality.

## Partial .git exposure

HEAD returns 'ref:' but objects 404: only refs are served. git_dumper
reports the refs; the honest record is 'refs-only, no object walk'. Don't
fabricate the missing tree — the filenames in refs/logs still carry signal.

## The archive that won't extract

A 200 on /backup.zip that fails unzip: the catch-all again (an HTML error
page). Check magic bytes before assuming a hit.

## 403 that means 'real but forbidden'

.htaccess-style rules often block dot-files by pattern: /.env 403s while
/.env.bak reads fine. A 403 pattern-match on dot-files is the strongest
signal that the file exists.

## Compression/dynamic catch-alls

The baseline body is dynamic (timestamped, randomized CSRF token): normalize
before diffing — strip the tokens, compare the structure.

## Recovered keys that are stale

An old .env.bak may hold rotated credentials — still evidence, but the chain
test decides impact.

## Sources with null sourcesContent

The map exists but `sourcesContent` is null: names/mappings without source
text — the bundle is the disclosure ceiling.

## Rate and scope limits

A shared instance rejects the sweep at request ~50 — the bounded list is the
whole budget; pick the most-likely paths first.

## The catch-all that IS the finding

A fallback route that echoes the request path inside a template is itself a
disclosure (path reflection) — different class, but record it.
