# Extended greps — additional extraction patterns

## The call-graph greps

```bash
# what calls an endpoint — the function context
grep -oE '.{120}/api/admin.{120}' b.js
# the axios/fetch call wrapping a path
grep -oE '(fetch|axios\.[a-z]+|\.request)\s*\([^)]{0,80}' b.js | grep -iE 'api|internal|admin|file|url'
# the method+path pairs
grep -oE '(axios|\$http)\.(get|post|put|delete|patch)\s*\(\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
```

## The baseURL/host greps

```bash
# axios baseURL — the API base
grep -oE 'baseURL\s*[:=]\s*["'"'"'`][^"'"'"'`]+' b.js
# a fetch wrapper's base
grep -oE '(api|API|BASE|base)_(URL|URL|url|host|endpoint)\s*[:=]\s*["'"'"'`][^"'"'"'`]+' b.js
# every host in the bundle
grep -oE 'https?://[A-Za-z0-9.-]+' b.js | sort -u
```

## The auth-flow greps

```bash
# where the token is stored/sent
grep -oE 'localStorage\.(set|get)Item\([^)]*\)' b.js | sort -u
grep -oE 'sessionStorage\.(set|get)Item\([^)]*\)' b.js | sort -u
grep -oE 'document\.cookie\s*=?\s*[^;]{0,40}' b.js
# the auth header construction
grep -oE '(Authorization|Bearer|X-[A-Za-z-]*[Tt]oken|api[_-]?[Kk]ey)["'"'"'\s:=]+[^,}]{0,40}' b.js | sort -u
# the jwt/token handling
grep -oE '(jwt|token|sign|verify|decode|refresh)\s*[.:(][^,}]{0,40}' b.js | sort -u
```

## The store/state greps

```bash
# a client state privilege flag
grep -oE '(is[Aa]dmin|is_admin|role|permission|level|isStaff|isSuperuser|canAdmin)\s*[:=]' b.js | sort -u
grep -oE 'state\.(user|auth|admin|role|permission)' b.js | sort -u
grep -oE '(store|getters|commit|dispatch)\.[a-zA-Z_]*[Aa]dmin' b.js | sort -u
```

## The hidden-route greps

```bash
# routes the UI hides — admin/internal/secret/debug named
grep -oE '"/?(admin|internal|secret|debug|hidden|private|manage|console|actuator|metrics|backup|dump|export|import|config|settings)[^"]*"' b.js | sort -u
# a gated component
grep -oE '(Admin|Internal|Secret|Debug|Manage|Console)[A-Z][a-zA-Z]*' b.js | sort -u
# a lazy import of a gated module
grep -oE 'import\(\s*["'"'"'`][^"'"'"'`]*(admin|internal|debug|secret)' b.js
```

## The SSRF-relevant greps

```bash
# a server-side fetch the client controls
grep -oE '(fetch|axios|http\.get|requests|urlopen|HttpClient)\s*\(\s*[^,)]*url' b.js | head
# an internal host
grep -oE 'https?://[a-z0-9.-]*(internal|\.svc|\.local|\.corp|10\.|192\.168|localhost|127\.|172\.1[6-9])[^"'"'"' ]*' b.js
# a webhook/callback URL param
grep -oE '[?&](url|uri|callback|webhook|target|dest|host|fetch|proxy|redirect)=' b.js | sort -u
```

## The mass-assignment-relevant greps

```bash
# extra keys the client sends that the UI omits
grep -oE '(role|admin|is_admin|isAdmin|permission|level|type|group|status|verified|balance|price|discount)\s*:\s*[^,}]+' b.js | sort -u
```

## The env/config inline greps

```bash
# the DefinePlugin/process.env inlined block
grep -oE 'process\.env\s*[:=]?\s*\{[^{}]{20,}' b.js
grep -oE 'process\.env\.[A-Z_a-z]+' b.js | sort -u
# a window-injected config
grep -oE 'window\.(__[A-Z_]+__|APP_ENV|CONFIG|ENV)\s*=\s*[^;]{0,100}' b.js
```
