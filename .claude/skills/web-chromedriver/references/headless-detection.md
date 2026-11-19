# Headless detection and anti-detection

## Why it matters

Two directions of the same problem:

- **Your local bot** must not be detectably "fake" if the challenge's
  anti-bot logic differs — a reproduction that the challenge's page
  rejects behaves differently than the real bot.
- **The challenge's bot** is itself a headless browser — understanding
  what makes it detectable tells you what environment your payload
  actually runs in (and sometimes how to confirm it is the bot and not
  a real user).

## The headless fingerprints

| Signal | Headless value | Normal value |
|---|---|---|
| `navigator.webdriver` | `true` | `undefined`/`false` |
| `navigator.plugins.length` | `0` | `>0` |
| `navigator.languages` | `["en-US"]` often | a real locale set |
| `window.chrome` | missing in old headless | present in real Chrome |
| `navigator.userAgent` | may contain `HeadlessChrome` | `Chrome/...` |
| WebGL / GPU renderer | `SwiftShader` (software) | a real GPU name |
| permissions / notifications | headless defaults | real defaults |

`navigator.webdriver === true` is the canonical tell — set by the
driver, not by a real browser.

## Reading the bot's environment

Your payload runs *inside the challenge's bot*, so reading its
environment from the payload tells you what you are working with:

```javascript
return {
  ua: navigator.userAgent,
  webdriver: navigator.webdriver,
  plugins: navigator.plugins.length,
  lang: navigator.languages,
  platform: navigator.platform,
};
```

Send it to your listener (or read it via `execute` in the local bot) —
it confirms whether the challenge's bot is headless Chrome, an old
version, or something else, and whether it is detectable.

## Anti-detection flags the bot may or may not set

| Flag | Hides |
|---|---|
| `--disable-blink-features=AutomationControlled` | `navigator.webdriver` stays `undefined` |
| a custom `--user-agent` | the `HeadlessChrome` UA |
| `stealth` plugins (puppeteer-extra) | most fingerprints |

If the challenge's bot runs automation-controlled disabled, your
payload cannot distinguish "bot" from "user" by `webdriver` — and
neither can you locally unless you reproduce that flag.

## When detection matters to the payload

Some challenge flows gate on "is this a real browser" — a payload that
fires only when `navigator.webdriver === false` behaves differently
in your local bot than intended. Reproduce the bot's flags exactly;
if the challenge bot hides `webdriver`, hide it locally too, or your
payload's environment diverges.

## The honest note

If you cannot determine whether the challenge's bot hides its
automation signals, say so — a payload that relies on
`navigator.webdriver` to detect the bot is fragile, and the notes
should record the assumption rather than present the detection as
certain.
