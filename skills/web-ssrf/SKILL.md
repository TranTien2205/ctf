---
name: web-ssrf
description: Prove server-side request forgery with a collector callback or an internal-only response — scheme sweeps, redirect and DNS tricks, and what a missing callback actually means. Use when a parameter takes a URL, a hostname, a webhook, an image source or an import path.
classes: ssrf
---

# Server-side request forgery

Proof requirement: **a callback at a collector we control carrying the probe
nonce, or a response only the internal network could have produced.**

## Start with what the fetcher accepts

One probe per scheme. The answer shapes everything after it.

| scheme | tells you |
|---|---|
| `http://` to our collector | the base case; a hit is the proof |
| `https://` | whether TLS is required, and whether the cert is checked |
| `file:///etc/passwd` | this is a file read as well, with its own class and proof |
| `gopher://`, `dict://` | arbitrary bytes to a TCP port: the dangerous case |
| `ftp://`, `sftp://` | often reachable where http is filtered |
| `http://[::1]/`, `http://127.1/`, `http://0/` | whether the loopback filter is a string match |

## The collector

```
proof.oob_start                     -> http://<our-addr>:<port>/<nonce>
<send the payload containing that URL>
proof.oob_check token=<nonce>
```

The hit records the **source address**, which is worth as much as the callback:
it tells you which host actually made the request, and whether it is the one you
were talking to or something behind it.

Our collector binds an interface on this machine. That is right for a lab or an
internal engagement and useless for an internet target with no route back — in
that case the honest options are an external collector the client approves, or
the internal-only response route below.

**No callback is not a negative result.** It may mean egress is blocked, which is
a separate, reportable measurement. Before concluding the class is absent, test
whether the host can reach anything at all.

## Internal-only responses, when there is no callback path

A response that could only have come from inside is evidence too: a cloud
metadata document, an internal hostname that does not resolve publicly, a
service banner on a port that is not exposed. Record it with
`extracted.internal_evidence` naming *why* it could not have come from outside.
Cloud metadata endpoints are the strongest version of this and also the most
sensitive — read the smallest document that establishes reachability, and do not
collect credentials you do not need.

## Filters, and the order to try them in

Cheapest first, and each one is a single probe:

1. the loopback and private-range aliases above
2. a hostname **you control** that resolves to a private address — defeats a
   filter that checks the string rather than the resolution
3. a redirect: your collector answers `302` to the internal target, which
   defeats a filter that validates only the first URL
4. a URL-parser differential: `http://expected.com@evil.test/`,
   `http://evil.test#expected.com`, fragments and backslashes — these work when
   the validator and the fetcher are different libraries

## Impact without over-reach

An SSRF that reaches only your collector is still a finding, and its impact
depends on what else is reachable — which needs a port measurement from the
inside, not a paragraph of speculation. "Could be used to reach internal
services" with no internal service named is a candidate, not an impact.
