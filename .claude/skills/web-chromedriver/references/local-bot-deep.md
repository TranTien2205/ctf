# Local bot deep — the reproduction engineering detail

## The property-extraction procedure

The bot's source is a spec — extract each property into a table before
writing the reproduction:

| Property | Extract from | Example |
|---|---|---|
| URL shape | the `goto`/`visit` arg | `userUrl` — your input verbatim |
| pre-visit actions | code before `goto` | `setCookie`, a login `fetch` |
| credential | the cookie/login it sets | `flag` cookie on the app domain |
| wait | `setTimeout`/`wait_for`/`sleep` | 5000 ms |
| flags | the `args`/`launch` array | `['--no-sandbox','--disable-gpu']` |
| browser version | `package.json`/Docker `FROM`/`image` | `chromium@120` |
| post-visit actions | code after the wait | `browser.close()`, a second `goto` |
| viewport | `setViewport`/window flag | `1280x800` |

A property not in the source is an assumption — mark it.

## The cookie-scope detail

The bot's flag cookie is the usual exfil target — reproduce its scope
exactly:

```python
# playwright — match name, domain, path, flags
page.context.add_cookies([{
    'name':'flag','value':'TESTFLAG',
    'domain':'localhost','path':'/',
    'httpOnly':False,           # does the bot set HttpOnly? -> changes how you read it
    'sameSite':'Lax',           # Lax/Strict drops it on cross-origin nav
}])
```

- `HttpOnly` -> `document.cookie` cannot see it; the jar can, and a
  same-origin request carries it
- `SameSite=Strict` -> dropped on a cross-origin navigation — your
  payload must run on the same site
- `domain`/`path` -> whether your URL's page even receives the cookie

A reproduction that sets the cookie wrong is testing a different bot.

## The wait-shape detail

The bot's wait is the payload's execution budget — reproduce its
*shape*, not just the duration:

| Bot waits on | Reproduce | Your payload must |
|---|---|---|
| `setTimeout(5000)` | `page.wait_for_timeout(5000)` | finish within 5 s of load |
| `networkidle` | `wait_for_load_state("networkidle")` | not hold connections open |
| `wait_for_selector` | `wait_for_selector` | possibly create the node |
| a promise/event | the same event | trigger the condition |

A `networkidle` bot *extends* its wait for every request your payload
makes — an exfil `fetch` that never completes keeps the page busy and
may change the bot's behaviour.

## The flag-injection point

Stand the challenge up locally when the handout supplies it — the
payload's injection point is the same field/context the live flow
uses, not a synthetic test page. A payload tested on a different page
or a different DOM structure may land in a different context than the
bot sees.

## The version-pinning detail

The bot's browser version changes behaviour — an old `--headless`
mode, a different JS engine, a different CSP. When the reproduction
diverges from live and the properties all match, the version is the
suspect — read it from `package.json`/Docker and run the same major
version locally.

## The assumptions record

Every property not read from source is an assumption — record them:

```
reproduction assumptions:
- wait: 5000ms (no source, chose default)
- cookie: "flag" HttpOnly=false (guessed)
- flags: --headless --no-sandbox (no source, chose common set)
- version: latest local Chromium (bot version unknown)
```

A "confirmed" payload on assumptions is weaker — the notes must carry
which properties were guessed.
