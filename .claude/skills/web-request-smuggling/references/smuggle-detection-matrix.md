# Smuggle detection matrix — the pair-vs-oracle table

## The matrix — which probe finds which pair

| Pair | Probe | Signal |
|---|---|---|
| CL.TE | `CL:6 TE:chunked body=0\r\n\r\nG` | hang |
| TE.CL | `CL:4 TE:chunked body=5c\r\nGET /404 ...` | next-request 404 |
| TE.TE | `TE:chunked + TE:cow` + 404-poison | obfuscation-dependent |
| CL.CL | `CL:4 CL:7 body=A=1&B=2` | differential |
| CL.0 | `POST /ignored CL:60 body=GET /marker` | next-response marker |
| H2.CL | h2 `content-length:0` + DATA | downgrade-desync |
| H2.TE | h2 `transfer-encoding:chunked` | downgrade-desync |
| fold | `?host=x%0d%0aX-Inj:%201` | injected-header echo |
| upgrade | `Upgrade: ws` + smuggle inside frame | tunneled-smuggle |
| CONNECT | `CONNECT internal:80` + raw request | tunnel-response |

## The repeatability — the 3x rule

A signal that repeats 3x + is absent on the control → `confirms`.
A single timeout → `inconclusive`.

## The control — the ordinary request

```text
POST / HTTP/1.1
Content-Length: 4

A=1&
```

The control — the same request without the ambiguity — the baseline —
`detection-oracle.md`.

## The matrix-of-false-positives — what looks like a desync

| Signal | Is it desync? |
|---|---|
| 400 on ambiguous request | NO — front rejected |
| 500 on ambiguous request | MAYBE — back errored |
| timeout once | NO — congestion? |
| timeout 3x + no-control-timeout | YES — CL.TE |
| 302 | NO — normal response |
| next-request 404 | YES — TE.CL |
| second response | YES — queue-poison |
| injected header echo | YES — fold, not smuggle |
| `Connection: close` | NO — no shared socket |

## The confidence-ladder — the evidence grades

1. `confirms` — a second response, or the smuggle's output lands
2. `inconclusive` — a repeatable-but-not-definitive signal
3. `denies` — a rejection or a missing prerequisite

## The order — the probe sequence

```text
1. crlf_probe.py — the fold-matrix
2. CL.TE hang — the timing probe
3. TE.CL 404 — the poison probe
4. TE.TE obfuscation — the matrix
5. CL.CL dup-CL
6. CL.0 body-ignored
7. upgrade-tunnel
8. h2 headers
```

`probe-sequences.md` — the full sequence.
