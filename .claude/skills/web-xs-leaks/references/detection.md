# Detection — is this an XS-leak target

The class's defining shape: a bot reads under the victim's session,
and you CANNOT read the response directly. The detection sequence
names the sub-shape and the channel.

---

## 1. The class's defining question

```text
a bot/victim's browser loads a page whose RESPONSE you can't read —
but a side-channel tells you something ABOUT it. the response is
opaque; a measurable difference (frame-count, error, timing, cache,
a server-side state change) leaks one bit or a character-set.
```

## 2. The two sub-shapes — classic vs sealed

```text
CLASSIC — the bot visits a URL YOU supply → your own page runs your
JS → the oracle is a client-side measurement (frame-count, error,
timing, cache).

SEALED — the bot visits a FIXED URL on the target, and CSP blocks
script → NO attacker JS runs → the oracle is a SERVER-SIDE state
change or a DECLARATIVE (CSS/HTML-only) oracle.

the deciding question: is there ANY origin, reachable by the bot,
on which I can run one line of JavaScript?
```

## 3. The detection probes — naming the sub-shape

```bash
# is there a bot endpoint that takes an attacker URL?
grep -rnoiE 'bot|admin|visit|report|puppeteer|playwright|selenium|headless' <src> | head -20

# does the bot take a URL, or a fixed path?
grep -rnoE 'bot\.|visit|open|goto|page\.|url.*=' <src> | head -20

# the CSP — can attacker JS run?
curl -s -i "$BASE/" | grep -i 'content-security-policy'
#   script-src 'none' → sealed (no JS); 'unsafe-inline'/'unsafe-eval' → JS runs

# a Chrome managed policy — URLBlocklist/URLAllowlist
grep -rnoiE 'URLBlocklist|URLAllowlist|managed.*policy|incognito|createIncognitoBrowserContext' <src> | head -10
```

## 4. The oracle-inventory — what can the bot's load leak

```text
the response's shape changes with the victim's data:
- a frame-count — one <iframe> per result → frames.length
- an error — a 200 vs a 404/500 → onload vs onerror
- a redirect — the URL changes → history/:visited
- a timing — a slow vs fast response → timing
- a cache — a fetched resource → cache-probe timing
- a size — a bigger vs smaller response → a size side-channel
- a server-state — a counter/store/counter++ → a recency/counter read
- a CSS-match — a selector that matches → a font/resource load
```

## 5. The server-side-channel inventory — the sealed case

```bash
# every mutation a plain GET can cause — the read-back surface
grep -rnoiE 'cache|store|counter|increment|get|set|lpush|rpush|expire|ttl|lru|evict|rate.?limit|quota|nonce|token|GETDEL' <src> | head -30

# the store's eviction policy — a recency channel
grep -rnoiE 'maxmemory|allkeys|lru|evict|policy' <src> | head -10

# a counter you can read back
grep -rnoiE 'counter|count|incr|next|seq|id.*\+\+' <src> | head -10
```

## 6. The CSS-oracle inventory — the declarative channel

```bash
# the reflected/CSS surface — can you inject a stylesheet?
grep -rnoiE 'style|css|custom.*css|stylesheet|<style|font-face|unicode-range|attribute.*selector' <src> | head -20

# the element that holds the secret — is it reflected in an attribute?
grep -rnoE 'data-|secret|token|value|attribute|secret.*=|token.*=' <src> | head -20
```

## 7. The oracle-feasibility questions — the arithmetic

```text
- how long does the secret live? a 60s TTL → the whole leak+decode
  must fit.
- what request rate do you need? thousands of markers need tens-
  hundreds rps; a flat throughput cap kills it.
- how many bits per visit? a one-shot token = 1 bit; a recency/
  counter = thousands.
- is the secret's character-set known? a sorted/limited alphabet
  reduces the search.
```

## 8. The control-pair requirement — the oracle's sanity check

```text
every oracle needs a CONTROL PAIR:
- a selector/input that ALWAYS matches → the 'leak exists' control
- a selector/input that NEVER matches  → the 'no leak' control
if the always-true and never-true don't separate → the channel
didn't work — a failed run, not a wrong answer.
```

## 9. The class-boundary — is it XS-leak or a neighbor

```text
a fetch READS the response            → web-cors (a data read)
a write fires under credentials        → web-csrf
a script runs in the target's origin   → web-xss
a side-channel MEASURES a difference   → web-xs-leaks ← this class
a cache serves a poisoned response     → web-cache-poisoning
```

## 10. The detection ledger — the sub-shape recorded

```bash
python3 tools/state.py <c> --hypothesis \
  "xs-leaks: <classic|sealed> — oracle=<channel> — secret=<target>"
```
