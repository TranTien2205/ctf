# Mechanism — what a headless browser is and why you drive it

## The two distinct uses

`web-chromedriver` covers two different things, and the skill only makes
sense once they are separated.

**Debugging aid** — you run a local headless browser yourself to
reproduce the challenge's admin bot. The live bot gives you a small
number of visits and no error output; a local browser gives you the
console, the DOM, the network log, and as many visits as you want. This
is the common case, and the reason the skill exists.

**Attack surface** — the challenge itself exposes a WebDriver endpoint
(a `chromedriver` or `geckodriver` port, a Selenium Grid, a `/session`
API). Then the driver is the target: a session can navigate to a
`file://` URL and the page source returns its contents — a file read as
whatever user launched the driver. This is rarer and always in scope
when it appears.

The skill does NOT cover general XSS payload construction — that is
`../web-xss/`. It covers the browser *control* layer: how to drive a
real browser, what it can tell you, and what it can reach.

## The WebDriver model

WebDriver is a W3C-standard HTTP+JSON protocol. A driver binary
(`chromedriver`, `geckodriver`, `msedgedriver`) listens on a port; a
client creates a session over HTTP and issues commands. Every client
library — Selenium, Playwright's CDP layer, Puppeteer, `curl` — is a
thin wrapper over the same commands.

```
client --HTTP--> driver:PORT --IPC--> browser process
         POST /session            (create)
         POST /session/{id}/url   (navigate)
         GET  /session/{id}/source (read DOM)
         POST /session/{id}/execute/sync (run JS)
         DELETE /session/{id}      (destroy)
```

The driver holds the browser process open for the session's lifetime.
A leaked session is a leaked browser — always `DELETE` when done.

## What the local browser buys you

| Question the live bot cannot answer | The local browser answers |
|---|---|
| Did my payload execute at all? | console output + thrown exceptions |
| Which context did the value land in? | the rendered DOM, not the raw response |
| Does the sanitiser run before or after my sink? | observe the order with a marker at each stage |
| Does my exfil request actually leave? | the network log, not a listener guess |
| Is my tunnel reachable by a headless client? | fetch your own URL from inside the driver first |

## The file-read primitive (attack surface)

A WebDriver session can navigate to any URL the browser process can
reach, including `file:///etc/passwd` or `file:///flag`. The page source
then returns the file's contents. The read runs as the user that
launched the driver — often root inside a challenge container.

```
POST /session {"capabilities":{...}}        -> sessionId
POST /session/{id}/url {"url":"file:///etc/passwd"}
GET  /session/{id}/source                   -> file contents
```

This is a capability, not a debugging aid — the same command set,
turned outward at the challenge. Once a file read exists, the follow-on
is `../file-read-primitives/`.

## The reproduction principle

The local bot is only useful when it matches the challenge's bot on the
things that matter: the URL it visits, the credential it authenticates
as, the wait time, the Chrome flags. Read the challenge's bot source
when supplied — it is usually a short script that names each of those.
When it is not supplied, reproduce what you can observe and record
which parts are assumptions.

A bot that runs `--headless --no-sandbox --disable-gpu` and waits five
seconds on your URL is reproduced exactly that way; a payload that
fires in a mismatched local bot may never fire in the real one.
