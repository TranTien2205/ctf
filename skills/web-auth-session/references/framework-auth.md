# Framework auth — per-stack idioms, defaults, and the classic bugs

Each framework's auth machinery has its own failure modes. This file is
the per-stack reference — what the default looks like, where it breaks,
and the greps that find the dangerous idiom.

---

## Flask / Python

**Default**: `flask.session` — signed `itsdangerous` blob in the cookie.

```python
app.secret_key = 'dev'          # leaked → forge
SESSION_COOKIE_SECURE = False   # http leak
SESSION_COOKIE_HTTPONLY = False # XSS reads it
SESSION_COOKIE_SAMESITE = 'None' # CSRF-able
```

- `itsdangerous` URLSafeTimedSerializer — `loads(cookie, max_age=...)`.
- Bug: `secret_key` in `app.py`/`.env`/`config.py`/`git log` → forge.
- Bug: `session['user_id']` set but no check on `session.get('_fresh')`.
- Bug: `login_required` decorator present on some routes, absent on
  others — grep `-L` for it.
- `flask-unsign` for offline forge:
  `flask-unsign --sign --cookie '{"_user_id":1}' --secret leaked`
- The session content is readable: `flask-unsign --decode --cookie '...'`
  reveals `_user_id`, `_fresh`, `csrf_token` — the claim names to forge.

```bash
grep -rn "secret_key\|SECRET_KEY\|session\[" --include='*.py' .
grep -rL "login_required\|jwt_required\|auth_required" --include='*.py' .
```

## Django

**Default**: `django.contrib.sessions` — server-side, `sessionid` cookie
with a 40-char base62 id. Table `django_session`.

- `SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'`
  flips to signed blob → `SECRET_KEY` leak → forge.
- `SECRET_KEY` in `settings.py`/`.env` — the forge key.
- `sessionid` expires via `SESSION_COOKIE_AGE` (default 2 weeks).
- Bug: `request.session['user_id']` written by custom code, never
  checked by `@login_required` — the custom session and Django auth
  diverge.
- Bug: `authenticate()` called but `login()` skipped — the user is
  validated but no session bound.
- Bug: `@permission_required` on `dispatch` only — other methods of the
  CBV are open.
- Bug: `settings.AUTHENTICATION_BACKENDS` includes a custom backend that
  returns a user on any password.

```bash
grep -rn "SECRET_KEY\|SESSION_ENGINE\|authenticate\|login(" --include='*.py' .
grep -rn "@login_required\|@permission_required\|LoginRequiredMixin\|PermissionRequiredMixin" --include='*.py' .
grep -rL "login_required\|LoginRequiredMixin\|permission_required\|PermissionRequiredMixin" --include='views.py' .
```

## Express / Node

**Default**: `express-session` — `connect.sid` cookie, signed with
`secret`. Store: MemoryStore (dev) / connect-redis / connect-mongo.

```javascript
app.use(session({secret:'dev', resave:false, saveUninitialized:false}))
// bugs:
// secret in app.js/.env → forge connect.sid
// resave:true + saveUninitialized:true → session on every request → fixation surface
// cookie.secure not set → http leak
// cookie.sameSite not set → CSRF
// MemoryStore in prod → restart loses sessions; also sid visible in heap dumps
```

- `passport.js`: `req.user` populated by `deserializeUser` — bugs in
  the deserializer (returns wrong user on id collision).
- `jsonwebtoken`: `jwt.verify(t, SECRET)` alg from header (confusion);
  `jwt.decode(t)` used for authz (dead).
- Bug: middleware `app.use('/api', auth)` mounted AFTER routes — later
  routes unprotected.
- Bug: `req.session.userId = user.id` set, but `req.session.destroy()`
  never called on logout.

```bash
grep -rn "express-session\|connect.sid\|req.session\|req.user\|jwt.verify\|jwt.decode\|jsonwebtoken\|passport" --include='*.js' --include='*.ts' .
grep -rn "cookie.secure\|cookie.sameSite\|cookie.httpOnly\|cookie.domain" --include='*.js' --include='*.ts' .
```

## Rails

**Default**: `_app_session` cookie — encrypted Marshal (Rails <7) or
JSON (7+). `secret_key_base` in `config/credentials.yml.enc` +
`master.key`, or `config/secrets.yml`.

- `secret_key_base` leak → decrypt, modify `user_id`, re-encrypt.
- `before_action :authenticate_user!` (Devise) — grep `-L` for
  controllers missing it.
- `protect_from_forgery` — CSRF token; `skip_before_action
  :verify_authenticity_token` is the tell.
- `session[:user_id]` — the claim name.
- `remember_token` (Devise) — `cookies.permanent.signed` — forgeable
  with `secret_key_base`.

```bash
grep -rn "secret_key_base\|session\[\|cookies\[" --include='*.rb' .
grep -rL "before_action.*authenticate\|before_action.*authorize" --include='*controller.rb' .
grep -rn "skip_before_action\|skip_before_filter" --include='*.rb' .
```

## Laravel / PHP

**Default**: `laravel_session` cookie — encrypted serialized session,
`APP_KEY` in `.env`.

- `APP_KEY=base64:...` leak → `decrypt()`/`encrypt()` round-trip →
  forge `user_id`.
- `PHPSESSID` (plain PHP) — `sess_<id>` files in `/var/lib/php/sessions`
  — readable via file-read primitive → hijack.
- `session()` helper / `$request->session()` — `auth()->user()` is the
  bound user.
- `middleware('auth')` / `Route::middleware('auth')` — routes outside
  the group are open.
- `Auth::login($user)` without `Auth::attempt` — login-by-object bug.
- `Gate::define` / `authorize()` / `$this->authorize()` — policy checks.
- `remember_token` — `recaller` cookie, `selector:validator`.

```bash
grep -rn "APP_KEY\|session(\|auth()->user\|Auth::login\|middleware('auth')\|Gate::" --include='*.php' .
grep -rn "remember_token\|recaller" --include='*.php' .
```

## ASP.NET / .NET

**Default**: `.AspNetCore.Session` (encrypted data-protection) + `.AspNetCore.Cookies` (auth cookie) or JWT bearer.

- `[Authorize]` / `[AllowAnonymous]` — controller/action attributes.
  `[AllowAnonymous]` on a method inside an `[Authorize]` class → open.
- `User.Identity.IsAuthenticated` / `User.IsInRole("Admin")`.
- `HttpContext.Session` — server-side by default.
- `SignInManager.SignInAsync` — the login call.
- `JwtBearerDefaults.AuthenticationScheme` — JWT middleware;
  `TokenValidationParameters` has the dangerous flags:
  `ValidateIssuerSigningKey=false`, `RequireSignedTokens=false`,
  `ValidateIssuer=false`, `ValidateAudience=false`,
  `ValidateLifetime=false`, `ClockSkew` too big.
- `MachineKey` (legacy .NET Framework) — `validationKey`/`decryptionKey`
  leak → `__VIEWSTATE` + auth cookie forge → see `web-deserialization`.

```bash
grep -rn "TokenValidationParameters\|ValidateIssuer\|ValidateAudience\|ValidateLifetime\|RequireSignedTokens\|ClockSkew\|MachineKey" --include='*.cs' .
grep -rn "\[AllowAnonymous\]\|\[Authorize\]\|IsInRole\|SignInAsync" --include='*.cs' .
```

## Spring / Java

**Default**: `JSESSIONID` — server-side, 32-hex or base64.

- `SecurityConfig` / `WebSecurityConfigurerAdapter` — the `authorizeRequests()`
  chain. Order matters: `antMatchers("/admin/**").hasRole("ADMIN")`
  must come before `anyRequest().permitAll()`.
- `@PreAuthorize("hasRole('ADMIN')")` / `@Secured("ROLE_ADMIN")` /
  `@RolesAllowed("ADMIN")`.
- `oncePerRequestFilter` JWT filters — the custom `keyfunc`/`parser`
  bugs live here (`Jwts.parser().parse()` without sig check).
- `RememberMeServices` — `remember-me` cookie, `key` in config.
- `SessionRegistry` — concurrent session control
  (`maximumSessions(1)`).
- Bug: `csrf().disable()` + state-changing GET.

```bash
grep -rn "antMatchers\|authorizeRequests\|hasRole\|hasAuthority\|@PreAuthorize\|@Secured\|csrf().disable\|maximumSessions" --include='*.java' .
grep -rn "Jwts.parser\|parseClaimsJws\|SigningKeyResolver\|setSigningKey" --include='*.java' .
```

## Go

**Default**: `gorilla/sessions` or `gin-contrib/sessions` — cookie store
signed/encrypted with `[]byte(secret)`.

- `jwt.Parse(t, keyfunc)` — `keyfunc` returning `nil` for `alg=none`,
  or returning the RSA *public* key for an HS token (confusion).
- `jwt.WithValidMethods` missing → alg from header.
- `c.Set("user", ...)` / `context.WithValue` — the context user.
- Middleware order: `r.Use(auth)` before vs after route registration.
- `securecookie` — the gorilla signer; `hashKey`/`blockKey` leaks.

```bash
grep -rn "jwt.Parse\|WithValidMethods\|keyfunc\|sessions.NewCookieStore\|gorilla/sessions\|securecookie" --include='*.go' .
```

## Ruby (non-Rails) / Sinatra / Padrino

- `rack.session` env — `session[:user_id]`.
- `use Rack::Session::Cookie, secret: '...'` — signed cookie; secret in
  code → forge.
- `jwt` gem — `JWT.decode(t, key, true, {algorithm:'HS256'})` — third
  arg `false` skips verify entirely.

```bash
grep -rn "Rack::Session\|session\[\|JWT.decode\|JWT.encode" --include='*.rb' .
```

## PHP (plain)

- `PHPSESSID` — `session_start()` — files in `session.save_path`
  (`/var/lib/php/sessions/sess_<id>` or `/tmp`).
- `session_regenerate_id()` — MUST be called on login; absence =
  fixation.
- `session.cookie_httponly`/`session.cookie_secure`/`session.cookie_samesite`
  ini settings.
- `session.serialize_handler` — `php` vs `php_binary` vs `php_serialize`
  — a `|` separator bug lets you write `|O:8:"User":...` into a session
  value → object injection on the *next* session load.

```bash
grep -rn "session_start\|session_regenerate_id\|session_id(\|ini_set.*session" --include='*.php' .
```

## The universal "bug is in the middleware order" pattern

Across every stack the same bug recurs: the auth middleware is mounted
*after* the route that needed it, or a route group escapes the group
that carried the middleware. The check:

- Flask: is `login_required`/`jwt_required` on EVERY route? `grep -rL`.
- Express: is `app.use(auth)` before ALL protected `app.METHOD` calls?
- Rails: does every controller have `before_action :authenticate`?
- Django: does every view have `LoginRequiredMixin`/`@login_required`?
- Laravel: is the route inside the `Route::middleware('auth')->group`?
- Spring: does `antMatchers` order put restrictive before permissive?
