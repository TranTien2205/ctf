# Detection map — every surface to surface mapping, exhaustively

The complete map from the observed signal to the poisoning surface.

---

## 1. The signal-to-surface map — what each observation names

```text
a 'proxy_cache|cache_key|X-Cache-Status' → an nginx cache
a 'vcl_hash|hash_data|Varnish'           → a Varnish cache
a 'cf-cache|cloudflare'                  → a Cloudflare cache
a 'X-Served-By: cache-<id>'              → a Fastly cache
a 'X-Cache: Hit from cloudfront'         → a CloudFront cache
a 'Rails.cache|cache_page|flask_caching' → an app-level cache
a 'Vary|vary'                            → the key's discriminator
a 'X-Forwarded|X-Original|X-Rewrite'     → an unkeyed-header surface
a 'Referer|User-Agent|Accept'            → a reflected-header surface
a 'settings|profile|dashboard|admin'     → a deception surface
a 'Cache-Control|no-store|private'       → a cacheable surface
a 'normalize|redirect|rewrite|path'      → a normalization boundary
```

## 2. The surface-to-class map — which surface names which class

```text
a stored response served to others    → web-cache-poisoning
a fetch that reads bytes              → web-cors
a write                               → web-csrf
a JS that runs on the target origin   → web-xss
a desync front-end/back-end           → web-request-smuggling
a parser difference                   → web-parser-differential
an opaque response + a side-channel   → web-xs-leaks
```

## 3. The surface-to-probe map — which probe for which surface

```text
an nginx cache           → the X-Cache-Status probe
a Varnish cache          → the X-Varnish probe
a Cloudflare cache       → the CF-Cache-Status probe
an unkeyed header        → the send-then-clean-request probe
a privileged page        → the authenticated-then-anonymous probe
a normalization boundary → the path-confusion probe
a keyed input            → the falsifier probe (a different class)
```

## 4. The surface-to-falsifier map — which falsifier for which surface

```text
an unkeyed input   → the clean-request reflects the marker (the falsifier)
a privileged page  → the anonymous request returns the privileged page (the falsifier: a 302)
a normalization    → the stored copy's response is the app's (the falsifier: same normalization)
a keyed input      → a per-input entry → a different class
```

## 5. The surface-to-blast map — which blast for which surface

```text
a public URL       → every visitor (a broad blast)
a cachebuster URL  → only your key's requests (a confined blast)
a privileged URL   → the privileged page's requester base (a deception)
a rare URL         → a small blast (only your key's requests)
```

## 6. The surface-to-vector map — which input for which surface

```text
a host-rewrite surface   → X-Forwarded-Host
a scheme-rewrite surface → X-Forwarded-Scheme
a path-rewrite surface   → X-Original-URL
a charset surface        → Accept-Charset
a reflection surface     → a reflected header (User-Agent, Referer)
a cookie surface         → an unkeyed cookie
an auth surface          → the authenticated GET
```

## 7. The surface-to-payload map — which payload for which surface

```text
a host-rewrite surface   → X-Forwarded-Host: <domain>
a scheme-rewrite surface → X-Forwarded-Scheme: <scheme>
a path-rewrite surface   → X-Original-URL: <route>
a charset surface        → Accept-Charset: <charset>
a reflection surface     → <payload> in a reflected header
a cookie surface         → Cookie: <name>=<payload>
an auth surface          → the authenticated GET
```

## 8. The surface-to-confirm map — which confirm for which surface

```text
an unkeyed input   → the clean-request marker reflects + a HIT
a privileged page  → the anonymous request returns the privileged page
a host-rewrite     → the stored copy's links carry your host
a charset          → the stored copy carries the charset-decoded payload
```

## 9. The surface-to-edge map — which edge for which surface

```text
a keyed input      → a per-input entry → a different class
a MISS reflection  → a reflection, not a store → a different class
a no-cache surface → no stored copy → a different class
a no-store surface → the page isn't cached → a different class
```

## 10. The surface-to-ledger map — what to record per surface

```bash
python3 tools/state.py <c> --hypothesis \
  "cache-poison-<surface>: input=<unkeyed> — key=<cached-parts> — blast=<shared-url>"
```
