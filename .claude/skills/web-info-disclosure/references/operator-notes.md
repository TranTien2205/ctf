# Operator notes — field-tested habits

## Before the sweep

- Baseline FIRST — every later read diffs against it. Skip it and the whole
  sweep reads as 'all 200, all hits' — they are not.
- Read the response headers before the paths: framework, version, proxy
  topology — they name which paths to try first.

## During

- Read bodies. Status 200 on /.env and status 200 on /notreal mean the same
  thing until content says otherwise.
- Note every filename the evidence gives you — a comment, a listing, an
  error path. Those are your only legitimate custom probes.
- 403 is not absence. It's the most interesting status here — the artifact
  exists and is forbidden; try the bypass list before moving on.

## On finding artifacts

- Grep, don't open — dumps and heapdumps are GBs.
- List archives before extracting.
- Found secrets: use them in the chain, redact in notes, never commit.

## After

- Record closed channels as negatives (with the probe that closed them).
- Record the catch-all signature for future passes.
- The artifact is evidence; the flag still needs a chain.
