# Onboarding — the first session with this skill

## The mental model

A WebDriver session is a remote handle on a real browser. Whose browser
determines the use:

- **yours** -> a debug harness with console, DOM, network
- **theirs** -> a file-read and loopback foothold

Everything else is detail.

## The first commands to learn

```bash
# create + destroy — the lifecycle you must always close
curl -X POST .../session -d '{"capabilities":{...}}'   # -> sessionId
curl -X DELETE .../session/$S                          # always

# the three reads you will use most
curl -X POST .../session/$S/url -d '{"url":"..."}'     # navigate
curl .../session/$S/source                             # read DOM/file
curl -X POST .../session/$S/execute/sync -d '{"script":"return ...","args":[]}'
```

Learn these cold — every primitive is one of them.

## The first exercise

1. run a local `chromedriver` (`which chromedriver`)
2. `POST /session` -> get a `sessionId`
3. navigate to a page -> `GET /source` -> read the rendered DOM
4. `execute` `return document.title` -> the title
5. `DELETE` the session

Five commands and you have the whole model — everything else is the
same commands pointed at `file://`, `localhost`, or a payload's page.

## The second exercise

Stand up a challenge's bot locally:

1. read the bot's source (URL, cookie, wait, flags)
2. run a local driver with the same flags
3. set the same cookie, navigate to the same URL, wait the same time
4. inject a `console.log` canary -> read the console

This is the debugging-aid loop — the skill's most common use.

## What not to learn first

- CDP — reach for it only when WebDriver cannot answer
- Playwright's full API — the four hooks are all you need
- Grid routing — only when the challenge runs a Grid

## The first mistake to avoid

Firing a guessed payload at the live bot. The local reproduction is
the whole point — develop there, fire once confirmed.

## Where to go next

- `workflow.md` — the ordered run
- `attack-surface.md` — when the endpoint is the target
- `payload-development.md` — the debug loop in detail
- `per-mechanism.md` — the primitive catalogue
