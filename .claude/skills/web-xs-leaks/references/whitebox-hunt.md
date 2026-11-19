# Whitebox hunt — where the XS-leak surface lives in source

The grep paths that find each oracle's surface.

---

## The bot — the victim-viewer surface

```bash
# the bot endpoint — a /report, a URL-submit, an admin-review
grep -rnoiE 'bot|admin|visit|report|url.*submit|review|flag.*cookie|secret.*cookie' <src> | head -20

# the browser launch — headless or real, incognito or managed
grep -rnoiE 'puppeteer|playwright|selenium|chromedriver|headless|incognito|browser|launch|newPage|goto|createIncognito|URLBlocklist|URLAllowlist|policy' <src> | head -30

# the bot's session — the flag-holder context
grep -rnoE 'cookie|flag|secret|token|admin|session|setCookie|Set-Cookie' <src> | head -20
```

```javascript
// the bot shape — Express + puppeteer
app.post('/report',async(req,res)=>{
  const b=await puppeteer.launch({args:['--incognito']});
  const p=await b.newPage();
  await p.setCookie({name:'flag',value:FLAG,domain:'.t'});
  await p.goto(req.body.url);   // the URL the attacker controls
});
```

```text
the greps that matter:
- 'goto|visit' — the URL the bot opens
- 'setCookie|cookie' — the flag-holder context
- 'incognito|headless' — the bot's isolation
- 'URLBlocklist|URLAllowlist' — a managed policy → a forced sealed shape
```

## The CSP — the channel's gates

```bash
# the CSP — what's allowed
grep -rnoiE 'content-security-policy|script-src|style-src|font-src|img-src|default-src|connect-src|unsafe-inline|unsafe-eval|nonce' <src> | head -20
```

```javascript
// the CSP surface — Express helmet
app.use(helmet.contentSecurityPolicy({directives:{
  'script-src':["'none'"],
  'style-src':["'self'","'unsafe-inline'"],
  'font-src':["'self'","*"],         // the exfil — a font host wildcard
}}));
```

## The reflected secret — the CSS-matchable surface

```bash
# an attribute the secret lands in — a CSS-selector target
grep -rnoE 'data-[a-z-]+|value=|placeholder=|secret.*=|token.*=|setAttribute' <src> | head -20

# the secret's rendering — a text node the @font-face reads
grep -rnoiE 'render.*token|token.*render|innerHTML|textContent|<div.*secret|id.*secret|secret.*div' <src> | head -20
```

```javascript
// the reflected-secret shape — a token in an attribute
res.send(`<body data-secret="${token}">...`)
// or a token in text — a @font-face target
res.send(`<div id="secret">${token}</div>`)
```

## The CSS-injection surface — the declarative channel

```bash
# a custom-CSS/theme surface — can you inject a stylesheet
grep -rnoiE 'custom.*css|theme|stylesheet|<style|style.*inject|@import|paper|note.*css|link.*stylesheet|href.*css' <src> | head -20

# a font-family / unicode-range — the @font-face channel
grep -rnoiE 'font-family|@font-face|unicode-range|font-src' <src> | head -10
```

## The server-state surface — the sealed channel

```bash
# a redis/LRU store — the eviction channel
grep -rnoiE 'redis|lru|maxmemory|allkeys|evict|cache|store|setex|expire' <src> | head -20

# a counter/quota — the read-back channel
grep -rnoiE 'counter|incr|quota|rate.?limit|limit|remaining|INCR|DECR' <src> | head -10

# a one-shot token — the single-use flag
grep -rnoiE 'GETDEL|GETEX|one.?shot|single.?use|nonce|consume|delete.*after|delete.*read' <src> | head -10
```

```javascript
// the redis-LRU shape — the eviction channel
redis.set(key,val,'EX',60);   // a TTL secret
// --maxmemory-policy allkeys-lru → every GET refreshes the key
```

```javascript
// the counter shape — the read-back channel
redis.incr('counter');        // a GET that increments a readable counter
```

```javascript
// the one-shot-token shape
redis.getdel(token);          // a GETDEL — 'did it survive' is one bit
```

## The classic-shape surface — the client-side measure

```bash
# a frame-count oracle — a per-result iframe
grep -rnoiE 'iframe|frame|render.*result|result.*frame|search.*iframe' <src> | head -10

# a status oracle — a 200/404 search
grep -rnoiE 'search|find|lookup|query|404|status|exists' <src> | head -10
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
```
