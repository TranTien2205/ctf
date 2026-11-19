# First hour deep — the sixty minutes, expanded

## 0–5 min: read the situation

```
supplied source? -> grep webdriver|chromedriver|bot|admin|puppeteer|playwright
bot flow?        -> a report/admin-visit trigger?
endpoint?        -> POST /session on :9515/:4444; GET :9222/json
```

Output: which use applies (surface, aid, or both).

## 5–15 min: the reproduction (debugging aid) OR the primitive map (surface)

**Aid**: extract the bot's spec — URL, cookie, wait, flags, version —
into a table. Build the local driver with the same. Verify it reaches
the same page live reaches.

**Surface**: run the primitive probes — `file://` read, `execute`
`1+1`, `localhost` nav, `GET /cookies` — note which are live.

## 15–30 min: develop / read

**Aid**: four hooks on -> canary -> staged markers -> iterate until
the payload fires in the reproduction.

**Surface**: locate the flag's surface (file/route/cookie/DOM/render)
-> read it through the live primitive -> the flag text.

## 30–45 min: the channel + the fire

**Aid**: check the exfil channel from inside the driver (`goto` your
own URL — is it your body or an interstitial?). Confirm the full
payload. Fire at the live bot once. Watch the listener.

**Surface**: the flag is already in hand from the read — gate it.

## 45–60 min: gate + close

- `tools/hooks.py pre-flag` the candidate
- `DELETE` every session
- kill local drivers
- record the working payload/channel + dead cells in the notes

## The timeline risks

| Minute risk | Cause |
|---|---|
| reproduction mismatch at min 15 | guessed properties, wrong flags — re-derive |
| payload won't fire at min 30 | the context is `../web-xss/`, not here |
| channel dead at min 40 | the interstitial — check before firing |
| a session leak | the `DELETE` was skipped |

## The honest hour

The hour is enough when the reproduction matches and the channel is
live — the common case. It runs long when the reproduction diverges
or the channel is dead; both are recorded in the kill map, not fought
past the budget.
