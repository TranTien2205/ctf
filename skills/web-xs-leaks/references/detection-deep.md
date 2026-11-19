# Detection deep — the XS-leak signals, exhaustively

Every signal that names the class, ordered by how cheap it is to find.

---

## The bot — the victim-viewer is the entry

```bash
# the bot endpoint — a /report, a URL-submit, an admin-review
grep -rnoiE 'bot|admin|visit|report|url.*submit|review' <src> | head -20

# the browser — headless or real
grep -rnoiE 'puppeteer|playwright|selenium|chromedriver|headless|incognito|browser|chrome|firefox' <src> | head -20

# the managed policy — a forced sealed shape
grep -rnoiE 'URLBlocklist|URLAllowlist|policy|managed|ExtensionInstall' <src> | head -10

# the bot's session — the flag-holder context
grep -rnoiE 'cookie|flag|secret|token|admin.*cookie|session' <src> | head -20
```

## The CSP — what the sealed shape allows

```bash
# the CSP — the channel's gates
grep -rnoiE 'content-security-policy|script-src|style-src|font-src|img-src|default-src|connect-src|unsafe-inline|unsafe-eval' <src> | head -20
```

```text
the CSP surface per directive:
  script-src 'none'           → NO attacker JS → the sealed shape
  style-src 'unsafe-inline'   → styles survive → the CSS oracle works
  font-src 'self' *           → an external font host → the exfil
  img-src 'self'              → a bg-image exfil blocked
  default-src 'unsafe-inline' → a broad hole → check each directive
```

## The reflected secret — the CSS-matchable surface

```bash
# an attribute the secret lands in — a CSS-selector target
grep -rnoE 'data-[a-z-]+|value=|placeholder=|secret.*=|token.*=' <src> | head -20

# the secret's rendering — a text node the @font-face reads
grep -rnoiE 'render.*token|token.*render|innerHTML|textContent|<div.*secret|id.*secret' <src> | head -20
```

## The server-state surface — the sealed channel

```bash
# a redis/LRU store — the eviction channel
grep -rnoiE 'redis|lru|maxmemory|allkeys|evict|cache|store' <src> | head -20

# a counter/quota — the read-back channel
grep -rnoiE 'counter|incr|quota|rate.?limit|limit|remaining' <src> | head -10

# a one-shot token — the single-use flag
grep -rnoiE 'GETDEL|GETEX|one.?shot|single.?use|nonce|consume|delete.*after' <src> | head -10

# a 'last seen'/timestamp — the recency channel
grep -rnoiE 'last.?seen|timestamp|time|recent|recency' <src> | head -10
```

## The CSS-injection surface — the declarative channel

```bash
# a custom-CSS/theme surface — can you inject a stylesheet
grep -rnoiE 'custom.*css|theme|stylesheet|<style|style.*inject|@import|paper|note.*css' <src> | head -20

# a font-family / unicode-range — the @font-face channel
grep -rnoiE 'font-family|@font-face|unicode-range|font-src' <src> | head -10
```

## The classic-shape surface — the client-side measure

```bash
# a frame-count oracle — a per-result iframe
grep -rnoiE 'iframe|frame|render.*result|result.*frame|search.*iframe' <src> | head -10

# a status oracle — a 200/404 search
grep -rnoiE 'search|find|lookup|query|404|status' <src> | head -10

# a timing oracle — a slow-vs-fast path
grep -rnoiE 'sleep|delay|slow|timeout|query.*time' <src> | head -10
```

## The signal-to-sub-shape map — which surface names which channel

```text
a script-src 'none'            → a sealed shape → CSS/server-state
a style-src 'unsafe-inline'    → the CSS oracle survives
a font-src wildcard            → the @font-face exfil
a redis LRU store              → the eviction channel
a counter/quota                → the counter channel
a one-shot token               → the single-use flag
a reflected secret attribute   → the CSS-selector oracle
a secret in text               → the unicode-range oracle
a /report that takes a URL     → the classic shape (if the bot opens it)
a managed policy URLBlocklist  → a forced sealed shape
```

## The class-boundary signals — when it's NOT an XS-leak

```text
a fetch READS bytes (a CORS read)      → web-cors
a WRITE (a state change)               → web-csrf
a JSONP endpoint (a script-tag serve)  → a real read primitive
a postMessage broadcast                → a real read primitive
a stored response (a cache)            → web-cache-poisoning
a bot that runs your JS + reads data   → web-xss (a real read)
```

## The negative signals — when the surface is dead

```text
- a script-src 'none' AND no style-src/font-src hole AND no server-
  state mutation → the sealed surface is dead → a different class
- an airgapped bot AND no server-state read → no exfil → a different
  class
- a secret not in an attribute AND not in text AND no server-state
  mutation → no channel → a different class
```
