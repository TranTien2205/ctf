# Onboarding deep — from zero to driving a browser

## The mental model, built up

Start with the simplest fact: a browser can be remote-controlled over
HTTP. The protocol is WebDriver — plain `curl`-able JSON. A driver
binary (`chromedriver`) sits between you and the browser; you send it
commands, it drives the browser, returns the results.

```
you --POST /session--> chromedriver:9515 --> a Chrome process
you --POST .../url {file:///etc/passwd}--> it --> Chrome loads the file
you --GET .../source--> it --> Chrome's rendered page = the file text
```

The whole skill is that one pattern, pointed at different targets.

## The first five commands (learn cold)

| Command | Does |
|---|---|
| `POST /session` | create a session -> `sessionId` |
| `POST .../url` | navigate to a URL (incl. `file://`) |
| `GET .../source` | read the rendered page |
| `POST .../execute/sync` | run JS in the page |
| `DELETE /session/{id}` | destroy the session |

Learn these — every primitive is one of them.

## Exercise 1: the file read

```bash
chromedriver --port=9515 &          # start a local driver
S=$(curl -s -X POST localhost:9515/session -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["value"]["sessionId"])')
curl -X POST localhost:9515/session/$S/url -d '{"url":"file:///etc/passwd"}'
curl -s localhost:9515/session/$S/source      # <- the file's text
curl -X DELETE localhost:9515/session/$S
```

You just did the attack-surface read — the file contents came back in
`source`.

## Exercise 2: the debug harness

```python
# reproduce a bot locally, observe the console/network
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox'])
    pg=b.new_page()
    pg.on("console",lambda m:print("console:",m.text))
    pg.goto("http://localhost/")
    pg.wait_for_timeout(3000)
    b.close()
```

You just did the debugging-aid use — the console the live bot hides.

## The first mistake to unlearn

Do not fire a guessed payload at the live bot to "see if it works".
That is the blind channel this skill exists to close. The local
reproduction is the point — build it first.

## The dependency

`which chromedriver` before anything — a missing driver fails at
session create, not at the payload. `chromedriver --version` must
match the browser's major version.

## Where to go

- `workflow.md` for the ordered run
- `attack-surface.md` when the endpoint is the target
- `local-bot.md` for the reproduction detail
- `quick-reference.md` for the commands card
