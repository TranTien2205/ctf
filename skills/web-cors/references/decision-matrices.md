# Decision matrices — the complete lookup tables for every CORS state

The condensed verdict tables — read the measurement, look up the
verdict and the next action.

---

## Matrix 1 — the ACAO+ACAC pair → the read's exploitability

```text
ACAO                ACAC       verdict                     next
reflected           true       CREDENTIALED READ — VULN    build the page
reflected           absent     non-credentialed read       public data only
null                true       opaque-origin read — VULN   a data:/sandboxed page
null                absent     non-credentialed            public only
*                   (any)      PUBLIC read — NOT vuln      a `*` endpoint
fixed (in list)     true       credentialed — VULN         if you can host there
fixed (not in list) true       closed                      the bypass battery
subdomain           true       subdomain read — VULN       a controlled sub
prefix/suffix       true       lookalike bypass — VULN     the bypass origin
absent              any        no CORS                     not the class
```

## Matrix 2 — the check-shape → the bypass to try

```text
check-shape           bypass                          page's origin
reflect               none needed                     any (evil.com)
null-allow            a null origin                   data:/sandboxed/file:
prefix                a lookalike suffix              target.com.evil.com
suffix                a lookalike prefix              eviltarget.com
substring             a containing origin             evil-target.com
subdomain-trust       a controlled subdomain          sub.target.com
regex-loose           a pattern bypass                whatever the regex allows
url-parse             an @/?/# confusion              a real evil.com page
strict allowlist      no bypass                       closed — pivot
```

## Matrix 3 — the credential-ride → whether the session attaches

```text
cookie SameSite     ACAC       credentialed read?
None+Secure         true       YES — the cookie attaches
Lax                 true       NO — doesn't attach cross-site
Strict              true       NO
no-SameSite         true       NO — Lax-by-default
any                 absent     NO — ACAC gates it
a Bearer credential any        needs a preflight + the token's source
```

## Matrix 4 — the page's origin → which delivery

```text
the read's allowed origin       the page's delivery
evil.com (any foreign)          an attacker-hosted page — a link/bot
null                            a data: URL / sandboxed iframe / file:
sub.target.com                  a controlled-sub page (XSS/takeover/CTF-sup)
target.com.evil.com             a lookalike-domain page
the target itself               a stored-XSS page — same-origin, no CORS needed
```

## Matrix 5 — the exfil constraint → which channel

```text
the bot's reachability          the exfil channel
reaches attacker.com            fetch/img/beacon — any
can't reach attacker.com        write-back / DOM-writeback / DNS
a fetch-blocking CSP            img/beacon/form — a no-CORS channel
a page-unload risk              sendBeacon
a large payload                 websocket / POST
an iframe context               postMessage
a screenshotting bot            DOM-writeback
a same-origin readback          write-back (a comment/profile)
```

## Matrix 6 — the endpoint's content-type → the read method

```text
content-type            the read method
application/json        .json()
text/html               .text() + a regex/scrape
text/plain              .text()
application/javascript  a <script src> — XSSI/JSONP
an image/binary         .blob() / .arrayBuffer()
```

## Matrix 7 — the preflight → which request shape works

```text
preflight's gate                  the request shape that works
permissive (reflects+allows)      any request — non-simple works
strict ACAO                       a simple request (GET/urlencoded POST)
strict ACAM                       a GET — the method ACAM doesn't cover
strict ACAH                       no custom headers — a simple request
a 405 OPTIONS                     a simple request — no preflight exists
```

## Matrix 8 — the CORS-closed → which alternate-read

```text
the target's surface              the alternate read
a JSONP endpoint                  a <script src> read
a JS-served endpoint              XSSI — a global-setter capture
a ws endpoint                     a websocket read — CSWSH
a postMessage broadcast           an iframe + a message listener
an XSS surface                    a same-origin read — CORS moot
a measurable side-channel         an XS-leak — the web-xs-leaks class
none of the above                 a different bug class — reclassify
```

## Matrix 9 — the evidence-level → the verdict grade

```text
measured                          the grade
an ACAO reflected + ACAC          a CANDIDATE — the read is possible
the exploit page reads YOUR data  a stronger candidate — not yet the vuln
the exfil arrives at your listener a CONFIRMS — the read is proven
the flag is in the exfil          a CONFIRMS + a flag — the solve
```

## Matrix 10 — the falsifier → the pivot

```text
falsifier                         the pivot
ACAO:* on sensitive endpoint      a public-read — not the vuln — pivot
ACAC absent + SameSite-gated      a non-credentialed read — pivot to a Bearer
strict allowlist + no bypass      closed — pivot to JSONP/XSSI/ws
preflight-strict + no simple path closed for non-simple — pivot to simple
endpoint returns public data      nothing sensitive — find a better endpoint
```
