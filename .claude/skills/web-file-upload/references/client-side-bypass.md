# Client-Side Bypass — when the check never leaves the browser

## Recognizing client-side validation

- `accept=".jpg,.png"` on `<input type=file>` — browser picker filter only
- JS `onchange` validating `file.name`/`file.type`/`file.size`
- a submit handler that calls `validateFile(f)` before `FormData.append`
- a "rejected" alert that never sends a request

Check: does the rejection produce network traffic? DevTools → Network —
no request = client-side only.

## The bypasses — pick the cheapest

1. **Send the request directly** — replay the multipart POST with
   `curl`/`requests`/Burp; the JS never runs
2. **Strip the handler** — DevTools → `getEventListeners(input,'change')`
   → remove; or override `input.onchange=null`
3. **Patch the validator** — console: redefine `validateFile` to `true`
4. **Use the browser's file API** — set `input.files` programmatically:
   `let f=new File([payload],'shell.php',{type:'image/jpeg'}); let dt=new
   DataTransfer(); dt.items.add(f); input.files=dt.files;` then dispatch
   `change` — the app's own pipeline sends it
5. **Edit the `accept` attr** — mostly irrelevant since (1) exists

## The "client+server double-check" tell

Client check passes, server still rejects — the server has its own layer;
client bypass just removes the first gate. Normal.

## When client-side is the only check (still common in CTF)

Direct replay wins outright — `curl -F 'f=@shell.php;type=image/jpeg'`.

## Falsifier

- the rejection produces a real server response — it was never client-side
