# Detection workflow — finding the XS-leak surface, step by step

The detection sequence — each signal, each grep, each surface.

---

## Step 0 — the entry — does a bot exist

```bash
# the bot — a /report, a URL-submit, an admin-review
grep -rnoiE 'bot|admin|visit|report|url.*submit|review' <src> | head -20
# the browser — headless or real
grep -rnoiE 'puppeteer|playwright|selenium|chromedriver|headless|incognito|JSDOM' <src> | head -20
```

```text
no bot → no XS-leak. a bot that takes a URL → a delivery surface.
a bot that only visits the target → a fixed-URL (sealed) case.
```

## Step 1 — the CSP — what's allowed

```bash
# the CSP — the channel's gates
grep -rnoiE 'content-security-policy|script-src|style-src|font-src|img-src|default-src|connect-src|unsafe-inline|unsafe-eval|nonce' <src> | head -20
```

```text
'script-src none' → the sealed shape is forced.
'style-src unsafe-inline' → the CSS oracle works.
'font-src self *' → the @font-face exfil works.
'img-src self' → a bg-image exfil is blocked.
```

## Step 2 — the reflected secret — is it CSS-matchable

```bash
# a secret in an ATTRIBUTE — a CSS-selector target
grep -rnoE 'data-[a-z-]+|value=|placeholder=|secret.*=|token.*=|setAttribute' <src> | head -20
# a secret in TEXT — a @font-face target
grep -rnoiE 'render.*token|<div.*secret|id.*secret|innerHTML|textContent' <src> | head -20
```

```text
a secret in an ATTRIBUTE → a CSS-attribute-selector oracle.
a secret in TEXT → a @font-face unicode-range oracle.
```

## Step 3 — the server-state surface — what mutates

```bash
# a redis/LRU store — the eviction channel
grep -rnoiE 'redis|lru|maxmemory|allkeys|evict|cache|store|setex|expire' <src> | head -20
# a counter/quota — the read-back channel
grep -rnoiE 'counter|incr|quota|rate.?limit|remaining' <src> | head -10
# a one-shot token — the single-use flag
grep -rnoiE 'GETDEL|GETEX|one.?shot|single.?use|nonce' <src> | head -10
# a 'last seen'/timestamp — the recency channel
grep -rnoiE 'last.?seen|timestamp|recent' <src> | head -10
```

## Step 4 — the CSS-injection surface — can you inject a stylesheet

```bash
# a custom-CSS/theme surface
grep -rnoiE 'custom.*css|theme|stylesheet|<style|style.*inject|@import|link.*stylesheet|font-family|@font-face|unicode-range' <src> | head -20
```

## Step 5 — the classic-surface — what the JS measures

```bash
# a frame-count surface — a per-result iframe
grep -rnoiE 'iframe|frame|render.*result|result.*frame|search.*iframe' <src> | head -10
# a status surface — a 200/404 search
grep -rnoiE 'search|find|lookup|query|404|status|exists' <src> | head -10
# a timing surface — a slow-vs-fast path
grep -rnoiE 'sleep|delay|slow|timeout|query.*time' <src> | head -10
```

## Step 6 — the delivery surface — does the page reach the bot

```bash
# the bot's URL — attacker-controlled or fixed
grep -rnoE 'goto|visit|url.*submit|report' <src> | head -10
# a managed-policy bot — a forced sealed shape
grep -rnoiE 'URLBlocklist|URLAllowlist|policy|managed' <src> | head -10
# the bot's session — the flag-holder context
grep -rnoE 'setCookie|cookie.*flag|flag.*cookie' <src> | head -10
```

## Step 7 — the exfil surface — does the data reach you

```bash
# can the bot reach your listener
curl -sI "https://attacker.com/listener" || echo "airgapped — a server-state channel"
# a write-back surface — a comment/note endpoint
grep -rnoiE 'comment|note|post|store|submit' <src> | head -10
```

## The signal-to-surface map — what each grep names

```text
a 'goto|visit' + a flag cookie        → a bot that reads under the flag session
a 'URLBlocklist|URLAllowlist'         → a managed policy → a forced sealed shape
a 'script-src none'                   → a sealed shape → CSS/server-state
a 'font-src.*\*'                      → the @font-face exfil
a 'style-src.*unsafe-inline'          → the CSS oracle survives
a 'redis.*lru|maxmemory.*allkeys'     → the eviction channel
a 'incr|counter'                      → the counter channel
a 'getdel|GETDEL'                     → the one-shot-token channel
a 'data-secret|value=|setAttribute'   → a CSS-selector target
a '<div.*secret|id.*secret'           → a text-node @font-face target
a 'iframe|frame|render.*result'       → a frames.length surface
a 'search|find|lookup|404'            → a status/timing surface
```

## The detection-check — is it really an XS-leak

```text
a fetch that READS bytes              → web-cors (a real read)
a WRITE                               → web-csrf
a JS that runs on the TARGET origin   → web-xss
a stored response                     → web-cache-poisoning
a JSONP/script-tag serve              → a real read primitive
a postMessage '*' broadcast           → a real read primitive
a `*` ACAO public read                → a CORS question
an opaque response + a side-channel   → web-xs-leaks (a measure)
```

## The falsifier — is the surface dead

```text
a sealed shape with no CSS oracle AND no server-state channel →
  a different class.
an airgapped bot with no server-state read → a write-back or a
  different class.
a secret not in an attribute AND not in text → no CSS channel.
a managed-policy bot with no declarative channel → a different class.
```
