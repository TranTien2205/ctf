# Framework deep-dives — the per-stack CSRF internals

The mechanics of each framework's CSRF defense — how the token is
generated, stored, checked, and where the check's logic gaps live.

---

## Django — the synchronizer

```python
# the defense: CSRF_COOKIE + csrfmiddlewaretoken — a session-bound
# token the form echoes; CsrfViewMiddleware compares the cookie/
# session to the form value.
# the holes:
@csrf_exempt                          # decorator — skips the check
CSRF_USE_SESSIONS = False             # cookie-based, not session —
                                      # a double-submit shape —
                                      # plant the cookie + match
CSRF_COOKIE_HTTPONLY = False          # JS reads the csrftoken cookie
CSRF_TRUSTED_ORIGINS = ['*.t.com']    # subdomain-trust — a sibling
# a GET view that writes — Django never CSRF-checks safe methods
def delete_view(request):             # reached via GET — no check
    obj.delete()
# the check is per-VIEW — a view without the middleware context
```

```bash
grep -rn 'csrf_exempt\|CSRF_USE_SESSIONS\|CSRF_COOKIE_HTTPONLY\|CSRF_TRUSTED_ORIGINS\|CsrfViewMiddleware\|csrf_token' <src>
```

## Flask / Flask-WTF — the session-bound token

```python
# the defense: CSRFProtect — a session token + form field
# the holes:
WTF_CSRF_ENABLED = False
csrf.exempt(blueprint)                # a whole blueprint off
@csrf.exempt                          # a route off
app.config['WTF_CSRF_TIME_LIMIT']=None # a non-expiring token —
                                      # replayable forever
# a form without {{ form.csrf_token }} + a validate_on_submit that
# isn't called — the check only runs in validate_on_submit
form.validate_on_submit()             # if the handler uses
                                      # request.form directly, no check
```

```bash
grep -rn 'WTF_CSRF\|csrf.exempt\|CSRFProtect\|validate_on_submit\|request\.form' <src>
```

## Express / csurf — the cookie+body double-submit

```javascript
// the defense: csurf — a _csrf token in cookie + body
// the holes:
csurf({ignoreMethods:['GET','HEAD','OPTIONS']})   // a GET write open
csurf({cookie:{httpOnly:false,sameSite:'none'}})  // a settable cookie
// a route mounted BEFORE app.use(csurf) — unguarded
app.post('/x',handler);app.use(csurf());          // x unguarded
// a token endpoint req.csrfToken() that's open
app.get('/token',(req,res)=>res.json({t:req.csrfToken()})) // a leak
// value:req.session vs cookie — the cookie shape is double-submit
```

```bash
grep -rn 'csurf\|ignoreMethods\|csrfToken\|_csrf\|app\.use' <src>
```

## Go / Gin — hand-rolled, the bind-tolerance

```go
// NO built-in CSRF — whatever the app wrote
// the common hole: ShouldBindJSON tolerates unknown keys — the
// text/plain JSON assembly works (the card's mechanism)
func handler(c *gin.Context){
    var obj struct{ A string `json:"a"` }
    c.ShouldBindJSON(&obj)            // extra keys ignored
}
// a remote_ip/localhost gate as the only check — the card's shape
if c.Request.RemoteAddr=="127.0.0.1" { ... }
// a token compared with == — a coercion or a global value
if c.PostForm("csrf")==stored { ... }
```

```bash
grep -rn 'ShouldBindJSON\|RemoteAddr\|ClientIP\|PostForm\|csrf' <src>
```

## Rails — the authenticity_token

```ruby
# the defense: protect_from_forgery — a session token
# the holes:
protect_from_forgery with: :null_session   # nulls the session but
                                           # PROCEEDS — the request
                                           # continues unauthenticated-
                                           # but-allowed — a partial-
                                           # fail shape
skip_before_action :verify_authenticity_token
protect_from_forgery except: [:action]
# API-mode apps — ActionController::API has no forgery protection
class Api < ActionController::API     # no CSRF at all
# a form_authenticity_token in a GET form — leaks via URL
```

```bash
grep -rn 'protect_from_forgery\|skip_before_action\|null_session\|verify_authenticity\|ActionController::API' <src>
```

## Spring — the synchronizer

```java
// the defense: _csrf via Spring Security's CsrfFilter
// the holes:
.csrf().disable()
.ignoringAntMatchers("/api/**","/webhook")
CookieCsrfTokenRepository.withHttpOnlyFalse()   // JS reads XSRF-TOKEN
// a GET-mapped write
@GetMapping("/transfer")                        // GET — no CSRF check
// the token in a cookie the SPA reads — a settable-cookie shape
```

```bash
grep -rn 'csrf\|ignoringAntMatchers\|CookieCsrfToken\|@GetMapping\|@RequestMapping' <src>
```

## Laravel — the VerifyCsrfToken middleware

```php
// the defense: _token field or X-XSRF-TOKEN header
// the holes:
protected $except = ['/api/*','/webhook'];      // exempted routes
Route::post('/x',...)->withoutMiddleware(VerifyCsrfToken::class)
// the XSRF-TOKEN cookie isn't HttpOnly — the SPA reads it — a
// same-origin JS can set the header; cross-origin needs a subdomain
// a route outside the 'web' middleware group — no CSRF
Route::post('/x')->middleware('api')            // api group = no CSRF
```

```bash
grep -rn '\$except\|VerifyCsrfToken\|X-XSRF\|withoutMiddleware\|middleware.*api' <src>
```

## ASP.NET — the antiforgery pair

```csharp
// the defense: __RequestVerificationToken cookie + field
// the holes:
[IgnoreAntiforgeryToken]                          // skips it
[HttpGet] public IActionResult Delete()           // a GET write
// the cookie is double-submit — a settable cookie opens it
// AutoValidateAntiforgeryToken missing on the controller
```

## The per-framework grep — the posture in one pass

```bash
# a single sweep for the defense + its holes
grep -rnoiE 'csrf_exempt|CSRF_USE|WTF_CSRF|csurf|ignoreMethods|protect_from_forgery|null_session|csrf\(\)\.disable|ignoringAntMatchers|\$except|IgnoreAntiforgeryToken|SkipCsrf|withoutMiddleware|xsrf_cookies|check_xsrf' \
  <src> | head -40
```

## The per-framework falsifier table

| Framework | The check that closes it |
|---|---|
| Django | no csrf_exempt + middleware + session-bound token |
| Flask | WTF_CSRF on + token + validate_on_submit called |
| Express | csurf on all methods + httpOnly cookie + SameSite |
| Go | a real session-bound token + strict bind + no localhost-only |
| Rails | protect_from_forgery :exception + no skips + not API-mode |
| Spring | csrf enabled + no ignores + token required |
| Laravel | no $except + token on every state-route |
| raw PHP | a session-bound token verified on the write |
