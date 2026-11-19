# Detection index — the ordered probe list

## In order of cost (cheapest first)

1. **Read the handout** — `grep` `webdriver|chromedriver|puppeteer|
   playwright|bot` in any supplied source. Answers both questions.
2. **`GET /status`** on `:9515`,`:4444` — is a driver listening? Version?
3. **`POST /session`** on `:9515` — can a session be created?
4. **`POST /session`** on `:4444` — is it a Grid?
5. **`GET /json`** on `:9222` — is CDP exposed?
6. **Find the bot flow** — a report form, an admin-visit trigger.
7. **`file:///etc/passwd`** navigate + `source` — the read primitive.
8. **`execute` `return 1+1`** — the JS primitive.
9. **`localhost` nav** — the loopback surface.
10. **`GET /cookies`** — the jar.

## The single combined probe

```bash
# one session-create answers the exposure question for that endpoint
curl -s -m5 -X POST http://T:9515/session -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
```

`sessionId` -> surface live, keep it; refused -> dead, next port.

## The reproduction-detection order

1. bot source supplied? -> copy URL/cookie/wait/flags verbatim
2. no source, flow observed? -> reproduce observed, flag assumptions
3. neither? -> the debugging-aid use is weak; record the assumption

## The falsifier probes (close the cells)

- `POST /session` refused on all ports -> cell 1 dead
- `file://` nav errors AND `execute` `fetch("file://")` fails -> cell 2
- `execute` `1+1` errors -> cell 3
- `localhost` nav shows nothing extra -> cell 4

## The decision tree

```
handout source? --yes--> grep for driver/bot -> reproduce OR find port
             \--no-> observe flow + probe ports -> reproduce OR find port

port answers POST /session? --yes--> attack surface -> primitive probes
                          \--no-> bot flow exists? --yes--> debugging aid
                                                \--no-> class dead
```

## Index to the depth files

| Found | Open |
|---|---|
| the endpoint | `attack-surface.md` + `per-mechanism.md` |
| the bot | `local-bot.md` + `payload-development.md` |
| a Grid | `grid-remote.md` |
| CDP | `cdp.md` |
| a blocked read | `evasion.md` + `troubleshoot.md` |
