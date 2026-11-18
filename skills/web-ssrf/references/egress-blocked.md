# Egress-blocked — the no-external-fetch model

The fetcher can't reach the internet — every external probe dies —
but the fetch still runs internally. Don't wait for a canary that
can never fire — pivot to the internal-echo channel immediately.

---

## 1. The diagnostic — is it really egress-blocked?

```text
send your canary → silence → then send the INTERNAL-probe:
  url=http://127.0.0.1:1/        → refused-error → the fetcher
                                   dialled → the class is live,
                                   just egress-blocked
  url=http://example.com/         → timeout → egress-blocked
                                   confirmed — an EXTERNAL fetch
                                   times out while internal works
the split — internal-dials, external-times-out → egress-filter —
  the fetcher reaches its own network only — the standard ctf
  air-gap shape
```

## 2. The proof-channel under no-egress — the internal-echo

```text
the callback is dead — the proof is internal-content:
  - body-echo of an internal-page — the route's content IS the
    evidence — the fetch echoes /admin or /flag
  - error-echo — the refused/reset strings — the internal-dial
    leaves evidence in the error
  - status-code — 200-internal vs 500/timeout-external — the
    differential
  - timing — the internal-connect vs the external-timeout
all four are internal-legs — the fetch proves itself inside
```

## 3. The flag-paths under no-egress — internal-first

```text
the flag lives inside — the question is WHERE:
  - the loopback-route — /flag on the app — or /admin/flag —
    the loopback-admin — the fetcher's own ip passes the check
  - a sibling-service — the other-container — the subnet-sweep —
    the sibling's flag-endpoint
  - a data-store — redis/memcached/es — the flag-key
  - a file — file:///flag — the read-path
  - the metadata-service — 169.254.169.254 — even "no-egress"
    containers may reach link-local — the metadata-IP is
    link-local — not "egress" — often reachable when the
    internet isn't!
```

The link-local exception: `169.254.169.254` is a LINK-LOCAL
address — the egress-firewall blocking internet-egress may still
let link-local through — the metadata-IP is reachable even when
the internet is dead — test it FIRST under egress-blocked.

## 4. The internal-subnet — what the host can see

```text
/proc/net/arp  via file:// → the neighbors — the subnet-map
/proc/net/fib_trie → the host's own IPs
the gateway — .1 — the host — the host-services — the docker-host
the compose-siblings — the service-names — internal-dns —
  http://sibling-name/ — the name resolves internally
```

## 5. The metadata-under-block — link-local reach

```text
169.254.169.254 is LINK-LOCAL — the egress-block may not cover
it — the link-local route is a different table —
  url=http://169.254.169.254/latest/user-data
  → reaches → the metadata → the flag-paths (user-data/iam)
  → the egress-block blocked the INTERNET not the metadata-net
```

## 6. The no-callback workflow

```text
1. internal-probe first — url=http://127.0.0.1:1/ → refused →
   the class confirmed — no canary needed
2. port-sweep the loopback — ssrf_probe --ports — the internal-
   service map
3. file://probe — file:///etc/passwd → file-read
4. metadata — 169.254.169.254 → cloud?
5. subnet — the compose-siblings + the gateway
the canary comes LAST — if at all — under egress-block it's
noise — the internal-legs are the work
```

## 7. The dns-canary exception — the dns-path

```text
even under egress-block, the RESOLVER may escape — the app's
dns-server is often reachable — the dns-lookup for your-name
goes out → your authoritative-DNS logs it → the dns-canary —
the weakest reachability-proof — "the server looked up my name"
— not a fetch — but a signal — under full-egress-block the
dns-path sometimes survives because the resolver is INTERNAL
to the vpc — the vpc-resolver reaches outside-dns differently
than the egress — try a unique-subdomain you control — the
dns-hit is the signal
```

## 8. The write-channel under no-egress — the shared-store

```text
no external-channel → the data goes through the internal-store:
  gopher→redis→SET a key → the web-app displays the key → the
    flag-VALUE passes through the STORE not the response —
    the write-read channel — blind-ssrf.md §6
  or the internal-service's own state — consul-kv — the kv-write
  the app's own display — a file-write to a served-dir —
    the webroot-write — gopher→redis→save→the-webroot
```

## 9. The "silence means egress-blocked" trap — other causes

```text
silence could also be:
  - the field isn't fetched at all — no-ssrf — the refused-error
    probe decides
  - the fetch is queued/deferred — webhook-shape — the fetch
    happens later — the canary fires eventually — check the
    history-page
  - the fetcher uses a proxy that blocks — the proxy-context —
    a different egress-path
  - DNS-blocked only — http-egress blocked, dns allowed — the
    dns-canary decides
  - the fetcher needs a specific-scheme — scheme-check first
the diagnostic order: internal-refused-probe → then external —
  the SPLIT is the diagnosis — silence on BOTH means "no fetch"
```

## 10. The working set under egress-blocked

```text
first three probes under no-egress:
  url=http://127.0.0.1:1/            — refused-error → the fetch
                                       class confirmed
  url=file:///etc/passwd              — file-read open?
  url=http://169.254.169.254/latest/  — metadata reachable?
the three tell you which-internal-world exists — the loopback,
the fs, the cloud — the chain picks from there
```

## 11. The full-airgap — no egress AND no metadata

```text
when 169.254.169.254 also fails → the flag is a FILE or an
INTERNAL-SERVICE — the file-map + the port-sweep — the flag
lives in the app's own container-network — the loopback-admin
or the sibling-service or the file-system
```

## 12. The dns-only-egress — the dns-canary detail

```text
a dns-canary requires YOUR authoritative-server — the public
rebinder/interactsh work — or your own zone — the dns-hit shows
the resolver's source-ip — the egress-ip — and proves resolution
ran — the dns-hit is NOT the fetch — it's the half-proof —
the fetch may still be blocked — the dns is the signal the
resolution happens — pair it with the internal-probe
```
