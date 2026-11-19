# Troubleshoot deep — the stubborn failure modes

## The version-skew trap

`chromedriver` must match the browser's *major* version. A mismatch
fails at session create with a version error — before any command:

```
session not created: This version of ChromeDriver only supports
Chrome version 120  (current browser is 121)
```

Fix: match the major version — `chromedriver --version` vs
`chrome --version`. On a managed env, the driver and browser are
usually pinned together; a hand-installed pair drifts.

## The container-flag trap

Inside a container, Chrome needs flags a desktop does not:

```
--no-sandbox --disable-dev-shm-usage --disable-gpu --headless=new
```

- `DevToolsActivePort file doesn't exist` -> missing `--no-sandbox`
  or `--disable-dev-shm-usage`
- crashes/hangs under load -> `/dev/shm` too small -> `--disable-dev-shm-usage`
- old headless renders nothing -> use `--headless=new`

## The leaked-session trap

A driver that "won't create a session" often has a leaked one holding
the browser:

```bash
curl -s http://localhost:9515/sessions      # list (non-standard)
curl -X DELETE http://localhost:9515/session/<id>
pkill chromedriver; pkill chrome            # the nuclear cleanup
```

The tell: `POST /session` hangs or errors, but `/status` answers.

## The frame-context trap

`execute` runs on the *current frame* — a payload in an iframe is
invisible to a top-frame `execute`. Symptom: the hook/script returns
nothing about the payload. Fix: `switch_to.frame` or `page.frame`
into the frame the payload lives in, then `execute`.

## The serialization trap

`execute` returns JSON-safe values only. Symptoms and the real types:

| You return | You get |
|---|---|
| a DOM element | `{"element-6066-...":"id"}` — a reference |
| `undefined`/`function` | `null` |
| a circular object | a serialisation error |
| a `Promise` | `null` (sync) or the resolved value (async+`awaitPromise`) |

For a DOM read, return `el.outerHTML`, not `el`. For async, use
`execute/async` + the callback.

## The pageLoad-hang trap

`navigate` waits for the `load` event by default — a page with a long-
lived connection (a kept-open fetch, a websocket, a stream) never
finishes loading and `goto` hangs past `pageLoad`. Fix: set
`pageLoadStrategy` to `eager` (`DOMContentLoaded`) or `none`, then
wait on a condition yourself.

## The interstitial trap (again)

A tunnel that inserts a confirm page works in *your* browser (you
click it) but not the headless client — the fetch to your tunnel gets
the interstitial HTML, not your listener. The fix is the channel:
fetch your own URL from inside the driver first; a body that is not
yours is a dead channel.

## The cookie-scope trap

An `add_cookie` with the wrong `domain`/`path` does not reach your
page — the cookie exists in the jar but is not sent to your URL.
Symptom: the payload's `document.cookie` lacks it. Fix: match the
bot's exact `domain` and `path`; verify with `GET /cookies` filtered
to the page's origin.

## The timing-race trap

A payload that races the page's own JS (reads a value before the app
sets it, fires before a handler binds) fails intermittently — works on
a slow local run, dies on the fast live bot. Fix: wait on the
condition (`wait_for_selector`, a poll for the value), not a fixed
delay.
