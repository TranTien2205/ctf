# Whitebox hunt — finding the auth bug in source

The auth bug is greppable. This file is the source-review checklist —
what to grep, per framework, and what the dangerous idiom looks like.

---

## 1. The universal greps

```bash
# the verify call — the source of truth
grep -rnE 'jwt\.(sign|verify|decode)|jwt\.decode|jsonwebtoken|pyjwt|jjwt|JwtBuilder|JwtParser' --include='*.py' --include='*.js' --include='*.ts' --include='*.java' --include='*.rb' --include='*.go' --include='*.php'

# algorithm allowlist
grep -rnE 'algorithms?[:=]|allowedAlgorithms?|allowed_algs?|verify_signature|verify_exp|verify_aud|verify_iss|verify_iat|verify_nbf|verify_jti|validate_aud|require' --include='*.py' --include='*.js' --include='*.ts'

# secret / key material
grep -rnE 'secret|SECRET|signing_key|private_key|public_key|JWT_|SESSION_KEY|APP_KEY|HMAC_' --include='*.py' --include='*.js' --include='*.ts' --include='*.env*' --include='*.yml' --include='*.yaml' --include='*.json' --include='*.env' --include='*.config*'

# session lookup and binding
grep -rnE 'session|sid|cookie|set_cookie|set-cookie|Set-Cookie|request\.cookies|req\.cookies|context\.user|ctx\.user' --include='*.py' --include='*.js' --include='*.ts' --include='*.rb' --include='*.java' | grep -iv 'test\|spec\|mock'

# header injection surface
grep -rnE 'kid|jku|x5u|x5c|jwk|jwks|header\[' --include='*.py' --include='*.js' --include='*.ts' --include='*.java' --include='*.rb'

# the authz check itself
grep -rnE 'role|is_admin|isAdmin|is_staff|is_superuser|has_permission|has_role|authorize|allowed|deny|require_role|require_admin|check_permission|permission_required' --include='*.py' --include='*.js' --include='*.ts' | grep -iv 'test\|spec\|mock'
```

## 2. The verify-call table — find yours

| Framework | Dangerous idiom | Safe idiom |
|---|---|---|
| **pyjwt** | `jwt.decode(t, key)` — alg from header | `jwt.decode(t, key, algorithms=["HS256"])` |
| **pyjwt** | `jwt.decode(t, key, algorithms=["HS256","RS256"])` — confusion | single alg only |
| **pyjwt** | `jwt.decode(t, options={"verify_signature":False})` | never |
| **jsonwebtoken (node)** | `jwt.verify(t, SECRET)` — alg from header | `jwt.verify(t, SECRET, {algorithms:['HS256']})` |
| **jsonwebtoken** | `jwt.decode(t)` for authz | `jwt.verify` |
| **jose (node)** | `jwtVerify(t, JWKS)` fetched by `jku` | pinned `getKey` callback |
| **jjwt (java)** | `Jwts.parser().parse(t)` — may skip sig | `parseClaimsJws` + `setSigningKey` |
| **jjwt** | `parserBuilder().setSigningKeyResolver()` that reads `kid` from file | resolver that validates path/allowlist |
| **java-jwt (auth0)** | `Algorithm.none()` accepted | `JWT.require(Algorithm.RSA256(k))` |
| **golang-jwt** | `jwt.Parse(t, func(t)(interface{},error){return key,nil})` returning wrong key type | `jwt.WithValidMethods([]string{"HS256"})` |
| **golang-jwt** | `keyfunc` returning `nil` for `alg=none` | reject `none` explicitly |
| **ruby-jwt** | `JWT.decode(t, nil, false)` — third arg `false` skips verify | `JWT.decode(t, key, true, {algorithm:'HS256'})` |
| **php-jwt (firebase)** | `JWT::decode($t, new Key($secret, ['HS256','RS256']))` | single `Key` alg |
| **System.IdentityModel (.NET)** | `RequireSignedTokens=false`, `ValidateIssuerSigningKey=false`, `ValidateAudience=false` | all `true` + pinned `IssuerSigningKey` |
| **Nimbus (java)** | `JWTClaimsSet` parsed without `verify` call | `RSASSAVerifier`/`MACVerifier` run |
| **lua-resty-jwt** | `jwt:verify(t, secret)` alg from header | pin `alg` in options |
| **Flask itsdangerous** | `serializer.loads(cookie)` — needs `SECRET_KEY` only | `SECRET_KEY` not in source/env |
| **Django signing** | `signing.loads(cookie, key=SECRET_KEY)` | same |

## 3. The session-store greps

```bash
# where does the session live?
grep -rnE 'SESSION_ENGINE|session.*store|session.*cache|Redis|Memcache|django\.contrib\.sessions|express-session|connect-redis|express\.session|session\s*=' --include='*.py' --include='*.js' --include='*.ts' --include='*.rb' --include='*.java' --include='*.yml'

# rotation on login?
grep -rnE 'regenerate|rotate|new_session|migrate|cycle|session_id\s*=' --include='*.py' --include='*.js' --include='*.ts' --include='*.rb'

# binding check?
grep -rnE 'remote_addr|remote_ip|X-Forwarded-For|User-Agent|request\.headers.*ip|request\.environ.*REMOTE' --include='*.py' --include='*.js' --include='*.ts'
```

## 4. The authz-middleware greps — where it SHOULD be

```bash
# Flask/Django decorator
grep -rnE '@login_required|@permission_required|@staff_member_required|@user_passes_test|@requires_auth|@require_admin|@jwt_required|@jwt\b|@auth_required' --include='*.py'

# Express middleware
grep -rnE 'requireAuth|requireAdmin|isAuthenticated|isAuthorized|checkRole|verifyToken|authenticate|protect|guard' --include='*.js' --include='*.ts'

# Spring/Guice
grep -rnE '@PreAuthorize|@Secured|@RolesAllowed|hasRole|hasAuthority|@AuthenticationPrincipal' --include='*.java'

# Rails
grep -rnE 'before_action.*authenticate|before_action.*authorize|load_and_authorize|can\?' --include='*.rb'

# the absence test — files with resolvers/handlers and NO authz
grep -rL 'requireAuth\|authenticate\|login_required\|jwt_required\|@PreAuthorize\|authorize' --include='*.py' --include='*.js' --include='*.ts' --include='*.java' --include='*.rb' .
```

The last grep is the highest-value: every file that serves a route and
doesn't mention authz is a candidate boundary miss.

## 5. The role-check greps

```bash
# how the privileged check is written
grep -rnE 'role\s*==|role\s*===|is_admin|isAdmin|admin\s*==|check_admin|\.role\b|\.isAdmin\b|hasRole|hasAuthority|\.permissions?\b|\.scope\b' --include='*.py' --include='*.js' --include='*.ts' --include='*.java' --include='*.rb'

# the privileged claim name
grep -rnE '"role"|'"'"'role'"'"'|"isAdmin"|'"'"'isAdmin'"'"'|"admin"|"sub"|"uid"|"user_id"' --include='*.py' --include='*.js' --include='*.ts'
```

Match the claim name in the source against what your token actually
carries — forge exactly that key.

## 6. The flag path greps

```bash
grep -rnE 'flag|FLAG|ctf\{|FLAG\{|CTF\{' --include='*.py' --include='*.js' --include='*.ts' --include='*.env*' --include='*.yml' --include='*.yaml' --include='*.json' --include='*.txt' --include='*.html' --include='*.ejs' --include='*.jinja*' | grep -v 'test\|spec\|mock\|node_modules'

grep -rnE 'admin.*flag|flag.*admin|/flag|/admin|secret.*flag|flag.*secret' --include='*.py' --include='*.js' --include='*.ts'
```

The flag location tells you which claim to forge — `role=="admin"` for
`/admin/flag`, `uid==1` for the first user's note, `tenant_id==0` for
the root tenant.

## 7. The middleware-file targets

The files where auth decisions live:

- `middleware/auth.js`, `middleware/authenticate.ts`, `middleware/guard.ts`
- `auth.py`, `auth.py` / `views/auth.py`, `security.py`
- `config/security.yml`, `config/application.rb` `before_action`
- `SecurityConfig.java`, `WebSecurityConfig.java`
- `app/controllers/concerns/authenticatable.rb`
- `server.js`/`app.js`/`index.js` — where `app.use(...)` mounts the auth

Read the file that *sets* `context.user`/`request.user`/`g.user` — the
bug is usually there (missing check), not in the resolver.
