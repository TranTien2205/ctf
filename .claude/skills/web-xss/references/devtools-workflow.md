# DevTools / local-browser workflow — test before you fire

For bot-triggered XSS you get limited shots — test the payload in
a local browser first. `web-chromedriver` skill covers driving a
local headless Chrome; this file is the working checklist.

---

## 1. The local test loop

```text
1. build the target page locally (or a copy of it)
2. inject your payload into the same context
3. open devtools — watch for errors/fires
4. iterate the payload until it fires
5. then submit to the bot
```

The reproduction: your payload in a local page that matches the
injection context (same tag/attr/script position, same CSP).

---

## 2. The "does it run?" sanity page

```html
<!-- test.html — paste your payload into the same context -->
<!doctype html><title>t</title>
<div>YOUR_PAYLOAD_HERE</div>
```

Load it in Chrome — `alert(1)` fires? the payload works. Silent?
check the console for errors. For the bot-context (headless), the
payload needs to not depend on user interaction.

`web-chromedriver` + playwright — drive the same page headlessly:

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
   b = p.chromium.launch()
   page = b.new_page()
   page.on('dialog', lambda d: d.accept())  # alert handler
   page.goto('file:///tmp/test.html')
   page.wait_for_timeout(500)
```

---

## 3. The "where did it land?" check — view-source vs DOM

```text
view-source: shows the RAW response — what the server sent
devtools Elements: shows the PARSED dom — normalized, sanitized
devtools Console: JS errors — why your payload didn't run
devtools Network: the outbound requests — did the beacon leave?
```

The critical distinction: the ELEMENTS panel shows the sanitized
DOM — your `<img onerror>` may show as `<img>` because the parser
ate the handler (or it fired and was removed). The VIEW-SOURCE
shows what the server actually sent — that's the ground truth.

---

## 4. The event-listener audit — what fires on what

```javascript
// devtools console — list all listeners on an element:
getEventListeners(document.querySelector('img'))
getEventListeners(document.body)
getEventListeners(window)
```

For postMessage sinks — `getEventListeners(window).message` lists
the listeners and their source files.

---

## 5. The CSP-audit — what the page actually allows

```javascript
// the page's effective CSP — check the header:
// devtools Network → response headers → Content-Security-Policy
// or: document.querySelector('meta[http-equiv]')?.content
```

Test the payload against the page's ACTUAL CSP — a payload that
works locally without CSP will fail when the target has
`script-src 'self'`.

---

## 6. The timing check — when does it fire

```javascript
// the bot's lifecycle: load → render → screenshot → close
// your payload must fire inside the load→render window —
// async work after the screenshot is dead

// test the timing: fire + how long until the request leaves?
// a fetch that resolves in 500ms may be cut by the bot's 2s window
```

Keep the exfil fast — sync beacons (img.src) fire immediately;
`fetch().then()` chains may outlast the bot's page-lifetime.

---

## 7. The headless-detection check — does the bot see it

```javascript
// headless Chrome differences:
navigator.webdriver === true      -- the automation flag
!!window.chrome                     -- chrome exists
navigator.plugins.length === 0      -- no plugins in headless
// don't fight these — the bot IS headless; your payload should
// work the same either way. the check matters for the OPPOSITE
// direction — a payload that only works with interaction is dead
```

---

## 8. The two-page test — your page + the target

For stored/bot flows:

```text
1. plant the stored payload on the target
2. locally: open your "bot-trigger" page that iframes/visits it
3. watch the exfil fire (or the listener log it)
4. the local run proves the chain end-to-end
```

`web-chromedriver` drives both pages — your trigger page and the
target — in one local browser to prove the chain.

---

## 9. The error-triage — when the payload doesn't fire

```javascript
// console errors to expect:
// "Refused to execute inline script" → CSP nonce/unsafe-inline missing
// "Refused to load the script"      → CSP src blocked
// "Uncaught SyntaxError"            → your JS is malformed
// "Failed to load resource"          → the exfil URL unreachable
// nothing at all                     → the tag never parsed — context wrong
```

Each error names the fix — CSP → different channel; syntax → fix
the payload; no-error-but-no-fire → wrong context.
