# Detection — is a WebDriver endpoint exposed, and is a local bot needed

## Two detection questions

1. **Is the challenge's admin bot worth reproducing locally?** Almost
   always yes when a client-side payload is involved — the live bot is
   a blind channel.
2. **Does the challenge itself expose a WebDriver endpoint?** Then the
   driver is the attack surface, not a debugging aid.

## Signatures of an exposed WebDriver endpoint

| Signal | Where |
|---|---|
| Port `9515`, `4444`, `9516`, `4723` open or proxied | port scan / challenge description |
| `POST /session` returns `{"value":{"sessionId":...}}` | direct probe |
| `chromedriver`, `geckodriver`, `selenium`, `webdriver` in source / banner / process list | white-box source, headers |
| A `/wd/hub` or `/session` route in the app | route map |
| `capabilities`, `browserName`, `goog:chromeOptions` in any request/response | source, proxy log |

The cheapest direct probe:

```bash
curl -s -X POST http://TARGET:9515/session \
  -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
```

A JSON `sessionId` in the response is the endpoint answering — a real
driver is listening. A connection refusal or 404 means it is not.

## Signatures a local bot is worth building

| Signal | Meaning |
|---|---|
| "Report to admin" / "the admin will visit" | a bot visits your URL — blind channel |
| A supplied bot script (bot.js, admin.py) | reproduce it exactly |
| A flag gated behind an action only the bot's browser can take | the payload must fire in a real renderer |
| CSP / sanitiser behaviour you cannot predict from source | observe it live in the local DOM |

## The reproduction-first check

Before any payload, confirm the local bot can reach the same page the
challenge's bot reaches. Navigate to the challenge's own URL from
inside your driver and read the page source back — if the page does
not render the same way, the reproduction is wrong and every later
payload test is on the wrong ground.

```bash
SESSION=$(curl -s -X POST http://localhost:9515/session \
  -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["value"]["sessionId"])')
curl -s -X POST http://localhost:9515/session/$SESSION/url \
  -H 'Content-Type: application/json' \
  -d '{"url":"http://CHALLENGE/"}'
curl -s http://localhost:9515/session/$SESSION/source | head -40
```

## Falsifier for the attack-surface use

The WebDriver endpoint use is killed when `POST /session` is refused,
the session cannot be created, or `navigate` to `file://` returns an
error the endpoint enforces. A refused session is not a "try a
different payload" signal — the class is dead at that endpoint.

## Budget

The detection work is cheap: one `POST /session` for the exposed-
endpoint question, one local navigate+source for the reproduction
question. Both answer inside a single probe budget. The expensive part
is the payload development loop afterward — that is where the five-
probe-per-mechanism budget applies, not to detection.
