# First hour — the sixty-minute playbook

## Minutes 0–5: classify the use

- read the handout: `webdriver|chromedriver|bot|admin` — which use?
- `POST /session` on `:9515`/`:4444` — is the endpoint exposed?

Decide: attack surface (endpoint answers) or debugging aid (bot flow).

## Minutes 5–15: attack surface — map the primitives

If `POST /session` answered:

- `nav file:///etc/passwd` + `source` — file read?
- `execute return 1+1` — JS?
- `nav localhost/admin` — loopback?
- `GET /cookies` — jar?

Each live primitive is a reach — note which answers.

## Minutes 15–45: attack surface — the read

- find the flag's surface (file? route? cookie? page?)
- read it through the live primitive
- the `source`/`execute`/`cookies`/`screenshot` carries the flag
- `tools/hooks.py pre-flag` the candidate

## Minutes 5–20: debugging aid — reproduce the bot

If a bot flow but no endpoint:

- read the bot source -> URL, cookie, wait, flags
- run a local driver with the same flags
- set the cookie, navigate, wait — verify the page matches live

## Minutes 20–50: debugging aid — develop the payload

- four hooks on (console/pageerror/request/response)
- canary first — does it execute?
- iterate on the four channels
- check the exfil channel from inside the driver
- confirm the full payload fires locally

## Minutes 50–60: debugging aid — fire and confirm

- fire the confirmed payload at the live bot once
- watch the listener for the flag-shaped value
- `tools/hooks.py pre-flag` the candidate

## The budget

The hour is generous — detection and reproduction are cheap. The cost
lives in the payload development loop and in a reproduction that
diverges from the live bot. Spend the early minutes on a faithful
reproduction; it pays back every later iteration.

## What eats the hour

- a reproduction that does not match -> re-derive the bot's properties
- a dead exfil channel -> the tunnel interstitial check
- a payload that needs more wait than the bot gives -> shorten it

Record each dead end in the kill map — the second hour starts from it,
not from zero.
