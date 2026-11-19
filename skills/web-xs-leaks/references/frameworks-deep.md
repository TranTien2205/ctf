# Frameworks deep — the XS-leak surface per stack, exhaustively

Each framework's bot, store, CSP, and CSS surface — the greps that find it.

---

## Express/Node — the dominant CTF stack

```javascript
// the bot — puppeteer
const puppeteer=require('puppeteer');
app.post('/report',async(req,res)=>{
  const b=await puppeteer.launch({args:['--incognito']});
  const p=await b.newPage();
  await p.setCookie({name:'flag',value:FLAG,domain:'.t'});
  await p.goto(req.body.url);   // the attacker-controlled URL
});

// a managed-policy bot — a forced sealed shape
const b=await puppeteer.launch({args:[
  '--incognito',
  '--managed-policy={"URLBlocklist":["*"],"URLAllowlist":["t.com"]}'
]});

// a redis LRU store — the eviction channel
redis.set(key,val,'EX',60);
// --maxmemory-policy allkeys-lru → every GET refreshes the key

// a counter — the read-back channel
redis.incr('counter');

// a one-shot token — GETDEL
redis.getdel(token);

// a CSP — helmet
app.use(helmet.contentSecurityPolicy({directives:{
  'script-src':["'none'"],
  'style-src':["'self'","'unsafe-inline'"],
  'font-src':["'self'","*"],
}}));
```

## Flask/Django — a redis/session channel

```python
# a flask_caching redis — the eviction channel
from flask_caching import Cache
cache=Cache(config={'CACHE_TYPE':'redis'})
# a counter or a rate-limit — a read-back channel
from flask_limiter import Limiter
limiter=Limiter(app,key_func=get_remote_address)

# the bot — a selenium/playwright
from selenium import webdriver
driver=webdriver.Chrome()
driver.get(url)   # the attacker-controlled URL
```

## Rails — a session/cache surface

```ruby
# a session/cookie store — a mutation surface
session[:token]=...
# a Rails.cache — an LRU recency
Rails.cache.write(key,val,expires_in:60.seconds)
# the bot — a selenium
driver=Selenium::WebDriver.for(:chrome)
driver.get(url)
```

## Go — a redis/in-memory store

```go
// a redis client — the eviction channel
rdb.Set(ctx,key,val,ttl)
// an in-memory map + a counter — a read-back
// the bot — a chromedp
chromedp.Run(ctx,chromedp.Navigate(url))
```

## PHP — a session/cache surface

```php
// a session — a mutation surface
session_start();
$_SESSION['token']=...
// a redis — the eviction channel
$redis->setex($key,60,$val);
// the bot — a headless chrome via a shell_exec
```

## The per-stack channel-inventory

```text
stack        the sealed channel           the CSS-injection surface
Express      a redis LRU / a counter      a reflected <style>/custom-css
Flask        a flask_caching redis        a template-injected <style>
Django       a cache/session              a template-injected <style>
Rails        a Rails.cache / session      a reflected <style>
Go           a redis / an in-memory map   a reflected <style>
PHP          a redis / a session          a reflected <style>
```

## The per-stack bot-config surface

```text
Express — a puppeteer.launch(args) — the incognito/managed flags
Flask   — a selenium/playwright — the driver.get(url)
Django  — a selenium/playwright
Rails   — a selenium
Go      — a chromedp — the chromedp.Navigate
PHP     — a headless chrome via a shell_exec
```

## The per-stack CSP surface

```text
Express — a helmet.contentSecurityPolicy — the directives object
Flask   — a Talisman or a manual header
Django  — a django-csp or a manual header
Rails   — a content_security_policy config
Go      — a manual header
PHP     — a header() call
```

## The per-stack grep-map

```bash
# Express — the bot + the store
grep -rnoiE 'puppeteer|redis|lru|maxmemory|getdel|incr|helmet|content-security' <src>
# Flask/Django — a redis/session
grep -rnoiE 'flask_caching|redis|session|limiter|selenium|playwright' <src>
# Rails — a session/cache
grep -rnoiE 'session|Rails.cache|redis|selenium' <src>
# Go — a redis/in-memory
grep -rnoiE 'redis|chromedp|Set|counter' <src>
```
