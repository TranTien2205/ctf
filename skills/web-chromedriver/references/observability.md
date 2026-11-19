# Observability — what the local browser can show you that the live bot cannot

## The four channels

A local headless browser exposes four observation channels the live
bot never does:

| Channel | What it shows | How to capture |
|---|---|---|
| Console | `console.log`, warnings, errors from your payload | `page.on("console")` / browser logs |
| Page errors | uncaught exceptions, thrown rejects | `page.on("pageerror")` / `window.onerror` |
| DOM | the rendered tree your payload lives in | `page.content()` / `GET /source` |
| Network | every request the page made | `page.on("request"/"response")` / CDP |

## Console and errors first

The first question is always "did my payload execute at all, and did
it throw." Both hooks are one-liners:

```python
page.on("console",   lambda m: print("CONSOLE:", m.type, m.text))
page.on("pageerror", lambda e: print("PAGEERROR:", e))
```

A `PAGEERROR: ReferenceError` means the payload's JS never ran — the
bug is in the payload or the context, not the channel. A clean
console with no exfil request means the payload ran but the exfil
branch did not — a different bug.

Over raw WebDriver, inject an error hook first:

```bash
curl -s -X POST .../execute/sync -d '{"script":"window.__e=[];window.onerror=m=>__e.push(m);return true","args":[]}'
# ... payload runs ...
curl -s -X POST .../execute/sync -d '{"script":"return window.__e","args":[]}'
```

## The rendered DOM

The response body and the rendered DOM are different documents —
sanitisation, JS rewriting, and template rendering all change the
latter. Read the DOM, not the response:

```python
print(page.content())        # playwright
print(driver.page_source)    # selenium
# raw: GET /session/{id}/source
```

Answers: which context did the value land in (attribute, script,
body), did the sanitiser strip or encode it, did the markup survive.

## The network log

The exfiltration question — "did the fetch leave" — is answered by
the request log, not by watching your listener:

```python
page.on("request",  lambda r: print("REQ:", r.method, r.url))
page.on("response", lambda r: print("RESP:", r.status, r.url))
```

A `REQ: GET https://your-tunnel/x?d=...` in the log is the exfil
working; its absence is the payload's failure, not the tunnel's. A
`RESP: 0` or a failed request is a CSP/mixed-content block — a
different fix than a payload bug.

## Timing

Match the bot's wait before judging a payload dead. A payload that
needs five seconds in a bot that waits two is a false negative —

```python
page.wait_for_timeout(5000)          # match the bot's wait
# or drive a real condition:
page.wait_for_selector("#flag")
page.wait_for_load_state("networkidle")
```

## Screenshot

The visual answer — what the page actually looked like — useful when
a payload's effect is layout or a rendered element:

```python
page.screenshot(path="after.png")
# raw: GET /session/{id}/screenshot -> base64 PNG
```

## CDP — deeper when needed

Playwright and Puppeteer expose Chrome DevTools Protocol for anything
the WebDriver API does not cover — JS coverage, precise network
interception, performance:

```python
client = page.context.new_cdp_session(page)
client.send("Network.enable")
client.on("Network.requestWillBeSent", lambda e: print(e["request"]["url"]))
```

Reach for CDP when the four channels above do not answer the question
— most payload debugging does not need it.
