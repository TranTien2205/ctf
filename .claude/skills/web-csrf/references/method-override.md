# Method override — reaching PUT/DELETE writes through a POST form

A cross-origin form sends GET or POST only. When the write lives on
PUT/PATCH/DELETE, the bridge is a method-override mechanism — a
parameter or header the app reads to re-route the method.

---

## 1. The problem

```text
a form's method attribute is GET or POST — nothing else. a PUT/
DELETE write can't ship from a form directly. the options:
- a method-override the app honors (_method, X-HTTP-Method-Override)
- a sibling route that accepts POST for the same write
- a framework that maps 'RESTful' routes onto POST + a hint param
```

## 2. The override conventions — the corpus

```text
# body/query parameter overrides — the form CAN send these
_method=PUT  _method=DELETE  _method=PATCH      (Rails, Laravel,
                                                Sinatra, some Express)
method=DELETE  method=PUT                       (some hand-rolled)
_methodOverride=PUT                             (some Spring)
X-Method-Override=PUT   — a HEADER — can't ship from a form
X-HTTP-Method-Override=DELETE — a header — can't ship from a form
X-HTTP-Method=PUT             — a header — can't ship
X-Original-Method             — a header — can't ship
_method tunnel via ? — GET /x?_method=DELETE    (the Lax-open shape)
```

The PARAMETER overrides ship in a form's body or query — the header
ones can't ship cross-origin (a custom header needs a preflight).

## 3. The framework override mechanisms

```ruby
# Rails — the _method parameter on a POST
#   POST /posts/1 with _method=DELETE → routed to destroy
#   the form: <input type=hidden name=_method value=DELETE>
```

```php
// Laravel — the same _method convention
//   POST /x with _method=PUT → routed to the PUT handler
//   Symfony: Request::enableHttpMethodParameterOverride()
```

```javascript
// Express method-override middleware
//   app.use(methodOverride('_method'))     — a body/query param
//   app.use(methodOverride('X-HTTP-Method-Override')) — a header —
//     the header form can't ship; the param form can
```

```python
# Django/Flask — no built-in; hand-rolled or a middleware
#   a custom middleware that reads _method and rewrites
#   environ['REQUEST_METHOD']
```

## 4. The override-audit — does the app honor it

```bash
grep -rnoiE '_method|methodOverride|X-HTTP-Method|X-Method-Override|enableHttpMethodParameterOverride|method_override|OVERRIDE' \
  <src> | head -20
```

## 5. The override in a form — the shapes

```html
<!-- Rails/Laravel PUT write -->
<form action="/posts/1" method=POST>
  <input type=hidden name="_method" value="PUT">
  <input name="title" value="x">
</form>

<!-- a DELETE write via _method -->
<form action="/posts/1" method=POST>
  <input type=hidden name="_method" value="DELETE">
</form>

<!-- a GET-tunneled method — the Lax-open shape -->
<script>location='https://t/posts/1?_method=DELETE'</script>
```

## 6. The GET-tunneled override — the Lax case

```text
a GET request with ?_method=DELETE — if the app honors the param
even on GET, the write ships as a GET → a top-nav attaches the Lax
cookie. the SameSite=Lax + a DELETE-write becomes reachable via a
GET override.
```

## 7. The override-vs-route check — does the re-route re-check

```text
does the method-override re-run the CSRF/auth middleware on the new
method? some frameworks re-check the overridden method; some treat
it as the original POST. the override that lands on a DIFFERENT
handler may skip the original handler's checks.
```

## 8. The falsifier

```text
the write is PUT/DELETE-only AND no _method/override mechanism
exists AND no POST sibling route — the write can't ship from a form
or a no-cors fetch (PUT/DELETE need a preflight). dead via browser
delivery; a stored page's fetch (same-origin) is the only shape.
```

## 9. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "method-override: _method=DELETE param reaches the DELETE write"
```
