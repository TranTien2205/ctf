# CDP — Chrome DevTools Protocol when WebDriver is not enough

## When to reach for it

WebDriver covers navigation, DOM, JS, cookies, screenshots. Reach for
CDP when you need what it does not expose: precise network interception,
request/response bodies, JS coverage, performance data, frame-level
control, or raw protocol access.

## Accessing CDP

```python
# playwright — a CDP session on a page
client = page.context.new_cdp_session(page)
client.send("Network.enable")
client.send("Page.enable")

# puppeteer — the page is already a CDP target
const client = await page.target().createCDPSession();
await client.send('Network.enable');

# raw — attach to --remote-debugging-port=9222
curl http://localhost:9222/json          # list targets
# then ws:// the webSocketDebuggerUrl
```

## The useful domains

| Domain | What it gives you |
|---|---|
| `Network` | every request/response with bodies, headers, timing |
| `Page` | navigation, frame tree, `captureScreenshot` |
| `Runtime` | `evaluate`, `callFunctionOn`, console events, exceptions |
| `DOM` | the live DOM tree, node search, outer HTML |
| `Fetch` | intercept and rewrite requests in flight |
| `Security` | certificate state |
| `Performance` | timing, metrics |

## Network capture with bodies

WebDriver's logs give you URLs; CDP gives you the bodies:

```python
client.send("Network.enable")
responses = []
def on_resp(e):
    responses.append(e["response"]["url"])
client.on("Network.responseReceived", on_resp)
# then for a requestId: client.send("Network.getResponseBody", {"requestId": rid})
```

Answers the exfil question *with the response body* — did the flag
page's response contain the flag, not just whether a request left.

## Intercepting requests

`Fetch.enable` pauses requests in flight — rewrite or mock them:

```python
client.send("Fetch.enable", {"patterns":[{"urlPattern":"*"}]})
def on_req(e):
    rid = e["requestId"]
    # inspect e["request"], then continue or fulfill:
    client.send("Fetch.continueRequest", {"requestId": rid})
client.on("Fetch.requestPaused", on_req)
```

Useful for: injecting a response the app expects, mocking a service
the challenge's bot would hit, or rewriting the CSP header to test a
bypass.

## JS evaluation without a wrapper

`Runtime.evaluate` runs JS and returns the object — richer than
WebDriver's serialised `execute` return:

```python
client.send("Runtime.evaluate", {
    "expression": "document.cookie",
    "returnByValue": True,
    "awaitPromise": True,      # resolves async — the big one
})
```

`awaitPromise` makes async evaluation natural — `Runtime.evaluate` on
`fetch('/flag').then(r=>r.text())` returns the resolved text, no
callback dance.

## The remote-debugging endpoint

`--remote-debugging-port=9222` opens CDP over HTTP+WebSocket —
**different** from the WebDriver port (`9515`). A challenge that
exposes `9222` is the same attack surface with a richer API: list
targets, attach, `Runtime.evaluate`, navigate via `Page.navigate`.

```bash
curl http://TARGET:9222/json          # targets -> webSocketDebuggerUrl
# attach over ws, then:
Page.navigate {"url":"file:///flag"}
Page.captureScreenshot
Runtime.evaluate {"expression":"document.body.innerText"}
```

## The honest limit

CDP is a debugging/power layer — most CTF payload work does not need
it. Reach for it when WebDriver's `execute`/`source`/`screenshot`
genuinely cannot answer the question, not as a default; the WebDriver
commands are the portable, simpler path and cover the common cases.
