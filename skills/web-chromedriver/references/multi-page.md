# Multi-page and frames — when the payload does not live on one page

## The frame problem

A payload inside an `<iframe>` runs in the frame's document, not the
top's — and WebDriver's `execute`, error hooks, and `source` operate
on the *current* frame. Commands must target the right frame:

```python
# selenium — switch into the frame first
driver.switch_to.frame(driver.find_element("css selector","iframe"))
driver.execute_script("return document.body.innerHTML")
driver.switch_to.default_content()     # back to top

# playwright — a frame object directly
frame = page.frame(name="content")     # or page.frames[i]
frame.evaluate("document.body.innerHTML")
```

## Error hooks per frame

An injected `window.onerror` catches errors only in its own document —
a hook on the top frame misses the iframe's payload. Inject into the
same frame the payload lands in, or inject into all frames:

```python
for f in page.frames:
    f.evaluate("window.__e=[];window.onerror=m=>__e.push(m)")
# ... payload ...
for f in page.frames:
    print(f.evaluate("window.__e"))
```

## top vs self navigation

The payload's `top.location` navigates the whole page; `self.location`
navigates its frame. An exfil that must carry the flag off the page
should use `top` or a `fetch`, not a frame-local navigation that
silently stays inside.

## The bot that visits several pages

A bot that navigates your URL *then* an internal page (to read a flag,
to log an action) means the payload's context may be destroyed by the
second navigation — or the flag you want is only reachable *after* the
bot reaches the second page. Reproduce the sequence, not just the
first visit:

```python
page.goto(your_url)         # your payload fires here
page.goto(internal_url)     # the bot then goes here — flag may live on this page
```

## Cross-origin frames

A frame from a different origin is opaque to the top's JS — the payload
in your frame cannot read the top's DOM if they differ in origin. The
bot's flag may live in the top document your frame cannot see; the
exfil then goes through what your frame *can* do (cookie exfil, a
top-navigation, a `postMessage`), not a DOM read.

## postMessage between frames

Frames communicate via `postMessage` — a payload in one frame can
receive the flag from another, or send a command up. Read the app's
`message` handlers; a missing origin check on the listener is `../web-
xss/`/`../web-csrf/` territory, but the harness work (which frame to
drive, where the listener lives) is here.

## New windows / popups

A payload that `window.open`s a new page creates a new browsing
context — a separate frame tree with its own document. Track the new
page in the reproduction (`page.wait_for_event("popup")` in Playwright,
`window_handles` in Selenium) if the flag or the exfil lands there.
