# Framework matrix — the XS-leak surface per stack

Each framework's XS-leak surface — where the side-channel lives and
the grep that finds it.

---

## The universal greps — the mutation+reflection surface

```bash
# the reflected secret — an attribute/element the CSS matches
grep -rnoE 'data-|secret|token|value|attribute|secret.*=|token.*=' <src> | head -20

# the CSS-injection surface — can you inject a stylesheet
grep -rnoiE 'style|css|custom.*css|stylesheet|<style|font-face|unicode-range' <src> | head -20

# the server-state mutation — the sealed channel's surface
grep -rnoiE 'cache|store|counter|incr|get|set|expire|ttl|lru|evict|nonce|GETDEL|rate.?limit' <src> | head -30

# the bot — the victim-viewer
grep -rnoiE 'bot|admin|visit|report|puppeteer|playwright|selenium|headless|incognito|URLBlocklist|URLAllowlist' <src> | head -20
```

## Express/Node — the bot + the store

```javascript
// a puppeteer bot
const puppeteer=require('puppeteer');
const b=await puppeteer.launch({args:['--incognito']});
await b.goto(url);            // the URL the attacker controls

// a redis store — the LRU-eviction channel
redis.set(key,val,'EX',60);   // a TTL secret
// --maxmemory-policy allkeys-lru → every GET refreshes the key
```

## Flask/Django — a redis/session channel

```python
# a redis-backed session or a cache — the LRU surface
from flask_caching import Cache
cache=Cache(config={'CACHE_TYPE':'redis'})
# a counter or a rate-limit — a read-back channel
```

## Rails — a session/cache surface

```ruby
# a session/cookie store — a mutation surface
session[:token]=...
# a cache — Rails.cache — an LRU recency
```

## Go — a redis/in-memory store

```go
// a redis client — the eviction channel
rdb.Set(ctx,key,val,ttl)
// an in-memory map + a counter — a read-back
```

## The per-stack channel-inventory

```text
stack        the sealed channel           the CSS-injection surface
Express      a redis LRU / a counter      a reflected <style>/custom-css
Flask        a flask_caching redis        a template-injected <style>
Django       a cache/session              a template-injected <style>
Rails        a Rails.cache / session      a reflected <style>
Go           a redis / an in-memory map   a reflected <style>
```

## The CSP surface — where the gates live

```bash
# the CSP — what's allowed
grep -rnoiE 'content-security-policy|script-src|style-src|font-src|img-src|default-src|unsafe-inline' <src> | head -20
#   script-src 'none' + style-src 'unsafe-inline' → CSS oracle works
#   font-src 'self' * → an external font host → the exfil
#   img-src 'self' → a bg-image exfil blocked → use font-src
```

## The bot-config surface — the delivery

```bash
# the bot's launch args — the context
grep -rnoiE 'puppeteer\.launch|playwright|browser.*launch|incognito|args:|--|headless' <src> | head -20
# the URL the bot visits — attacker-controlled or fixed
grep -rnoE 'goto|visit|open|page\.|url.*=' <src> | head -20
```

## The per-stack oracle-selection

```text
a redis LRU store          → the eviction channel — high bandwidth
a counter/state endpoint   → the counter channel — a few bits
a one-shot token           → the single-use flag — one bit
a reflected CSS attribute  → the CSS-selector oracle — a char-set
a unicode-range surface    → the @font-face oracle — a char-set
a strict CSP + no channel  → a different class
```
