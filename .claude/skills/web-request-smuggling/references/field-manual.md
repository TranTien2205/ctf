# Field manual — the operator's sequence

## The 60-second triage

```bash
curl -sv http://t/ 2>&1 | grep -iE "via:|server:|x-backend|x-cache"
```

A `Via:`/`X-Backend-Server:`/`X-Cache:` header names the proxy — the
front+back pair is live — the desync class is open.

## The 5-minute probe stack

```bash
python3 tools/web/crlf_probe.py --url "http://t/?host={M}" --value "ex.com"
```

Then the CL.TE timing probe, then the TE.CL 404-poison, then the
obfuscation matrix — `detection.md`.

## The byte-count rule

`Content-Length` = bytes between `\r\n\r\n` and end-of-body — every
`\r\n` = 2 — count exactly, never estimate — `cl-te-desync.md`.

## The chunk-grammar

```text
<hex>\r\n<data>\r\n0\r\n\r\n
```

Hex sizes, CRLF-delimited, `0\r\n\r\n` terminates — `chunked-encoding.md`.

## The readback — the next request's response

The smuggle's output goes to the NEXT request — the self-poison `GET /`
after the smuggle — `response-poisoning.md`.

## The flag — the verbatim excerpt

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<the verbatim excerpt>"
```

## The ledger — the state calls

```bash
python3 tools/state.py <name> --bug-class web-request-smuggling
python3 tools/state.py <name> --hypothesis "CL.TE via chunked"
python3 tools/state.py <name> --strategy-used chain_match
python3 tools/hooks.py post-probe <name> --request "..." \
  --verdict confirms --evidence-kind class --class web-request-smuggling \
  --hypothesis-id h1 --evidence "<excerpt>" --response "<raw>"
```

## The common failure — the ordering

Don't craft the smuggle before the desync pair is identified — the
pair determines whether the smuggle is a full second request (TE.CL)
or a prefix (CL.TE) — `workflow.md`.

## The escalation — budget exhausted

`chain_match` → `reclassify` → `writeup_search` → `novel_plan` →
`fanout_sweep` → `solver_handoff` — each with `state.py --strategy-used`.
