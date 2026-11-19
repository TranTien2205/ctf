# Local bot reproduction — matching the challenge's admin bot

## Why reproduce instead of firing blind

The live admin bot gives you a handful of visits and no error output.
Every payload fired at it is a coin flip you cannot inspect. A local
bot turns the same payload into a normal debugging loop: console,
errors, DOM, network — then only confirmed payloads spend a bot visit.

## Read the challenge's bot source first

When the handout supplies the bot script (commonly `bot.js`,
`admin.py`, `visit.js`, `bot/`), it names every property that matters:

- **URL it visits** — and how the URL reaches it (form field, POST,
  your report submission).
- **Credential it authenticates as** — a session cookie it sets before
  visiting, a flag in `document.cookie`, an admin login it performs.
- **Wait time** — `sleep(5)`, `page.wait_for_timeout(3000)`, a
  `setTimeout`. Your payload has that long to fire.
- **Chrome flags** — the `args` array or the launch command.
- **What it does before/after** — visits a login first, closes over a
  flag page, holds a cookie you must not clear.

A typical challenge bot, deconstructed:

```javascript
// bot.js — read this as a spec, not a mystery
const browser = await puppeteer.launch({
  args: ['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'],
});
const page = await browser.newPage();
await page.setCookie({name:'flag', value:'FLAG{...}', domain:'challenge', path:'/'});
await page.goto(userUrl, {timeout: 10000});
await new Promise(r => setTimeout(r, 5000));   // <-- your payload's budget
await browser.close();
```

The local reproduction copies each property exactly:

```python
# playwright reproduction of the bot above
browser = p.chromium.launch(headless=True, args=[
    '--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
page = browser.new_page()
ctx = page.context
ctx.add_cookies([{'name':'flag','value':'TESTFLAG','domain':'localhost','path':'/'}])
page.goto(my_payload_url)
page.wait_for_timeout(5000)
```

Use `TESTFLAG`, not the real flag — the local bot is a test harness.

## When no bot source is supplied

Reproduce what you can observe, and record the assumptions:

| Property | How to observe it | Assumption if hidden |
|---|---|---|
| URL it visits | your submission field, the app's report flow | the URL you submitted |
| Credential | the flag is probably a cookie on the bot | a `flag`/`session` cookie |
| Wait time | a report that "takes a few seconds" | 5 s is the safe default |
| Flags | response headers (`X-Chrome`, `via`) | `--headless --no-sandbox` |

Say which parts are assumptions in the challenge notes — a payload
that fires only because you guessed a longer wait is a false positive.

## The reproduction loop

```
1. stand up the challenge locally if source is supplied (docker compose / the handout)
2. run the local bot against YOUR copy — navigate to the challenge page
3. inject your payload into the same field the live flow uses
4. observe: console, errors, DOM, network
5. iterate until the payload fires in the local bot
6. only then fire it at the live bot once
```

## What to observe per iteration

```python
page.on("console",  lambda m: print("CONSOLE:", m.text))
page.on("pageerror",lambda e: print("PAGEERROR:", e))
page.on("request",  lambda r: print("REQ:", r.method, r.url))
page.on("response", lambda r: print("RESP:", r.status, r.url))
```

The four hooks answer the four blind questions: did it run, did it
throw, what did it fetch, what came back.

## The tunnel reachability pre-check

Before any exfil payload, verify a headless client can reach your
tunnel at all. Some tunnels (ngrok free, some port-forwarders) insert
an interstitial page a headless browser cannot pass. Fetch your own
URL from inside the driver:

```python
page.goto("https://your-tunnel.example.com/ping")
print(page.content())   # does it show your ping body, or an interstitial?
```

`tornadoservice` records losing attempts to exactly this — check the
channel before spending a bot visit on it.
