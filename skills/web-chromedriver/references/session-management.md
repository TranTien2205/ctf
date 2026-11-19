# Session management — lifecycle, leaks, and shared instances

## The lifecycle

```
create (POST /session) -> use -> destroy (DELETE /session)
```

Every session holds a browser process. The `DELETE` is not optional —
a leaked session leaks the browser, and on a shared or resource-bound
endpoint it can hold the only slot.

## Always delete, always finally

```python
try:
    driver.get(url)
    # ... work ...
finally:
    driver.quit()   # DELETE /session — runs even on exception
```

```bash
# curl — capture the id, always delete it
S=$(curl -s -X POST .../session -d '{...}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["value"]["sessionId"])')
# ... use $S ...
curl -s -X DELETE http://localhost:9515/session/$S
```

## Detecting a leaked session

A driver that refuses new sessions or hangs on `POST /session` often
has a leaked one holding the browser. `GET /sessions` (non-standard
but common) lists active sessions on some drivers:

```bash
curl -s http://localhost:9515/sessions
curl -s -X DELETE http://localhost:9515/session/<leaked-id>
pkill chromedriver   # the nuclear cleanup — kills all its browsers
```

## Shared-instance discipline

On a shared challenge endpoint:

- one session at a time — a Grid/single driver may serialise
- delete the instant you finish
- do not hold a session open "in case" — it blocks others and burns
  the host's memory
- if another session is leaked and you did not create it, note it —
  killing another team's session is a shared-instance write

## Timeouts as a safety net

Even with clean deletes, set a session `timeouts` so a hung command
does not pin the browser:

```json
{"timeouts":{"script":15000,"pageLoad":15000,"implicit":3000}}
```

A `pageLoad` timeout stops a `file://` crawl or a hanging navigation
from holding the session.

## Reattaching vs recreating

`goog:chromeOptions.debuggerAddress` attaches a session to an already-
running Chrome — useful for reconnecting to a bot's browser state, or
for a long-lived browser you re-drive. Most CTF use is create-and-
destroy; reattachment is for when the browser's state (cookies, open
pages) must persist across sessions.

## The bot's own sessions

A challenge's admin bot creates and destroys sessions each visit —
they are not yours to hold. Do not interfere with the bot's session
lifecycle; your local sessions are a separate driver process. On an
exposed endpoint that IS the challenge's driver, your sessions share
the bot's driver — be careful not to exhaust its session capacity or
the bot stops working for everyone.
