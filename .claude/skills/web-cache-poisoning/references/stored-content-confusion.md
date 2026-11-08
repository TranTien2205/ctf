# Stored-content confusion

A file uploaded for one purpose is fetched in a context that parses it as
another — the cache or static layer serves it with a content type or route the
writer never intended. The payload is a *polyglot*: valid under two parses.

## Probe that worked (Chromatic Aberration — confirmed)

Upload an XSSI/JSON/SVG polyglot whose body starts `")]}',\n` (the JSON-hijack
prefix) and contains an SVG branch:

```json
")]}',
{"svg":"<!DOCTYPE svg><svg xmlns=\"http://www.w3.org/2000/svg\"></svg>"}
```

Then:

```text
GET /api/media/raw?id=<asset>&workspace=<W>
GET /api/workspaces/manifest?workspace=<W>
```

Expected: the raw fetch serves the polyglot with a content type the consumer
parses as the *other* format — JSON-prefixed bytes executing as markup, or
SVG active content in a route that claims `application/json`. Falsifier: the
stored bytes are served with a strict, sniff-proof content type and the second
route rejects them.

## Why the polyglot shape matters

- `")]}',\n` breaks naive JSON consumers while staying inert to XML/SVG
  parsers — one file, two valid interpretations.
- `Content-Type` + `X-Content-Type-Options: nosniff` is the deciding gate: a
  route missing nosniff lets the browser pick the dangerous parse.
- The upload's *serving route* and *consuming route* may differ — find both in
  source or recon before firing.

## Falsifier

Uploads are stored but always served as `application/octet-stream` or with
`nosniff`, or the consuming route re-validates the format — the two-parse gap
is closed.

## Traps

- Place the stored content first, then poll or trigger the consuming route —
  bots and caches both run on schedules (recorded trap).
- The polyglot only works when overlaid at the offset the scanner/consumer
  reads — a leading byte change can invalidate one of the two parses.
