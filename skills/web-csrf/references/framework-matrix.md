# Framework matrix — the CSRF surface per stack

Each framework's default CSRF posture, its opt-out patterns, and
the grep that finds the hole.

---

## Django

```python
# the defense: csrfmiddlewaretoken, session-bound synchronizer
# the holes:
@csrf_exempt                      # the decorator that disables it
CSRF_COOKIE_HTTPONLY = False      # JS can read the token cookie
MIDDLEWARE missing 'django.middleware.csrf.CsrfViewMiddleware'
CSRF_TRUSTED_ORIGINS wildcard     # any subdomain trusted
# a GET view that writes — Django doesn't CSRF-check safe methods
def change(request):              # called via GET — no CSRF check
    obj.delete()                  # a GET-with-side-effect
```

```bash
grep -rn 'csrf_exempt\|CSRF_COOKIE_HTTPONLY\|CsrfViewMiddleware\|CSRF_TRUSTED_ORIGINS\|ensure_csrf_cookie' <src>
```

## Flask / Flask-WTF

```python
# the defense: WTF_CSRF via flask_wtf
# the holes:
WTF_CSRF_ENABLED = False
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
@csrf.exempt                     # exempt a blueprint/route
# no flask_wtf at all — Flask has NO built-in CSRF
# a form endpoint without {{ form.csrf_token }} + validate_on_submit
```

```bash
grep -rn 'WTF_CSRF\|csrf.exempt\|flask_wtf\|CSRFProtect' <src>
```

## Express / csurf

```js
// the defense: csurf middleware
// the holes:
app.use(csurf({ignoreMethods:['GET','HEAD','OPTIONS']})) // a GET write
// csurf cookie not HttpOnly → JS reads it
// cookie:{sameSite:'none'} or missing → the double-submit cookie
//   is settable cross-site
// a route mounted BEFORE the csurf middleware — unguarded
// csurf on /api but the write is on /internal
req.csrfToken()                  // the token endpoint — is it open?
```

```bash
grep -rn 'csurf\|csrf\|ignoreMethods\|csrfToken\|_csrf' <src>
```

## Gin / Go

```go
// NO built-in CSRF — whatever the app hand-rolled
// the holes:
//   no token check at all
//   a token compared with == (timing/coercion)
//   ShouldBindJSON tolerant of unknown keys — the text/plain JSON
//     assembly works (the TornadoService card's shape)
//   a localhost/remote_ip gate as the only check — the bot card
if c.Request.RemoteAddr == "127.0.0.1" { ... }  // the socket-peer gate
c.ShouldBindJSON(&obj)             // tolerant — extra keys ignored
```

```bash
grep -rn 'ShouldBindJSON\|RemoteAddr\|ClientIP\|csrf\|X-CSRF' <src>
```

## Rails

```ruby
# the defense: authenticity_token + protect_from_forgery
# the holes:
protect_from_forgery with: :null_session   # null_session SKIPS —
                                           # the session is nulled
                                           # rather than rejected —
                                           # the request PROCEEDS
                                           # unauthenticated-but-allowed
skip_before_action :verify_authenticity_token
protect_from_forgery except: [:action]     # an action exempted
# API mode without forgery protection
```

```bash
grep -rn 'protect_from_forgery\|skip_before_action\|verify_authenticity\|null_session' <src>
```

## Spring

```java
// the defense: _csrf synchronizer via Spring Security
// the holes:
.csrf().disable()                        // in the security config
.ignoringAntMatchers("/api/**")          // a whole prefix exempt
// CookieCsrfTokenRepository.withHttpOnlyFalse() — JS reads it
// a GET-mapped write — Spring doesn't CSRF-check GET
@GetMapping("/transfer")   // a write on GET — no CSRF check
```

```bash
grep -rn 'csrf().disable\|ignoringAntMatchers\|CookieCsrfToken\|withHttpOnlyFalse\|@GetMapping.*transfer\|@GetMapping.*delete' <src>
```

## Laravel / PHP

```php
// the defense: _token field + VerifyCsrfToken middleware
// the holes:
protected $except = ['/api/*', '/webhook'];  // exempted routes
// X-XSRF-TOKEN cookie not HttpOnly — the SPA token is JS-readable
// a route outside the web middleware group — no CSRF at all
Route::post(...)->withoutMiddleware(VerifyCsrfToken::class)
```

```bash
grep -rn '\$except\|VerifyCsrfToken\|X-XSRF\|withoutMiddleware' <src>
```

## ASP.NET

```csharp
// the defense: __RequestVerificationToken cookie+field
// the holes:
[IgnoreAntiforgeryToken]                 // attribute skips it
[AutoValidateAntiforgeryToken] missing   // a controller without it
// a GET action that writes
[HttpGet] public IActionResult Delete()  // GET write — no check
```

```bash
grep -rn 'IgnoreAntiforgeryToken\|ValidateAntiForgeryToken\|AutoValidateAntiforgery' <src>
```

## Angular / the SPA pattern

```text
the defense: XSRF-TOKEN cookie + X-XSRF-TOKEN header — the SPA
reads the cookie and echoes it as a header. cross-origin JS can't
read the cookie — BUT:
- the cookie isn't HttpOnly → a same-origin (subdomain) XSS reads it
- the server compares cookie to header — a double-submit — control
  both via a cookie-plant and it validates
- SameSite on the XSRF cookie matters — a missing-SameSite XSRF
  cookie can be SET cross-site via a subdomain/injection
```

## FastAPI / Starlette / aiohttp / Tornado

```python
# FastAPI: NO built-in CSRF — a dependency or hand-rolled
# Tornado: xsrf_cookies setting
self.settings['xsrf_cookies'] = True     # the defense
xsrf_cookies = False                     # off — the TornadoService
                                         # card's app had it off
def check_xsrf_cookie(self): pass        # a no-op override
# aiohttp: no built-in — a middleware or hand-rolled
```

```bash
grep -rn 'xsrf\|xsrf_cookies\|check_xsrf\|CSRFProtect\|csrf' <src>
```

## Ruby Sinatra / Rack

```ruby
# the defense: rack-protection's AuthenticityToken
# the holes:
disable :protection              # rack-protection off entirely
set :protection, except: :csrf   # CSRF specifically off
use Rack::Protection::AuthenticityToken  # absent → no check
```

## The PHP-no-framework shape

```php
// raw PHP — CSRF is whatever the app wrote
if ($_POST['csrf'] !== $_SESSION['csrf']) die();  // the only check —
                                                  // is it present?
// no check at all → raw $_POST reads → fully open
```

## The grep-corpus — finding the CSRF posture

```bash
# the defense's name in source — what mechanism exists
grep -rnoiE 'csrf|xsrf|_token|authenticity_token|RequestVerificationToken|anticsrf|forgery|SameSite|samesite|csrfmiddlewaretoken' \
  <src> --include='*.py' --include='*.js' --include='*.ts' \
  --include='*.rb' --include='*.php' --include='*.java' \
  --include='*.go' --include='*.cs' | head -60
```

The absence of any token mechanism in a state-changing app = the
open case. The presence of an exemption/ignore/null-session = the
partial-check case.

## The framework→falsifier table

| Framework | Falsifier |
|---|---|
| Django | csrf_exempt absent + middleware present + token session-bound |
| Flask | WTF_CSRF on + token required + not exempted |
| Express | csurf on all methods + HttpOnly cookie + SameSite |
| Gin | a real token check + strict bind + no localhost-gate |
| Rails | protect_from_forgery :exception + no skips |
| Spring | csrf enabled + no ignores + token required |
| Laravel | no $except + token required |
| raw PHP | a session-bound token verified on the write |
