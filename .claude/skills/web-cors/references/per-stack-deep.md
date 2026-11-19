# Per-stack deep — the CORS misconfig, framework by framework

The exact code, grep, probe, and bypass for every major stack — the
operational detail a real audit needs.

---

## Express + `cors` middleware — the Node canonical

### The default — `cors()` — public `*`

```javascript
const cors = require('cors');
app.use(cors());   // ACAO: * on everything — public read, never credentialed
```

A `*` endpoint reads public data — NOT the vuln.

### The vuln — `origin:true` + credentials

```javascript
app.use(cors({origin:true, credentials:true}));
// 'true' = reflect the request's Origin; credentials:true = ACAC:true
// → ANY origin reads the credentialed response — THE vuln
```

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
#   ACAO: https://evil.com  ACAC: true  → THE VULN
```

### The allowlist — the correct config

```javascript
var allowlist = ['https://app.target.com','https://admin.target.com'];
app.use(cors({
  origin: function(o, cb){
    if(allowlist.indexOf(o) !== -1 || !o) cb(null, true);
    else cb(new Error('CORS'));
  },
  credentials: true
}));
```

A fixed allowlist — closed unless a bypass exists.

### The bypassable check — a function that validates loosely

```javascript
app.use(cors({
  origin: function(o, cb){
    if(o && o.endsWith('target.com')) cb(null, o);   // SUFFIX — eviltarget.com passes
    else cb(null, false);
  },
  credentials: true
}));
```

```bash
curl -i -b "$CJ" "$BASE/api/x" -H 'Origin: https://eviltarget.com'
#   ACAO: https://eviltarget.com  → the suffix check passed
```

### The regex — `origin: /regex/`

```javascript
app.use(cors({origin: /\.target\.com$/, credentials:true}));   // subdomain-trust
app.use(cors({origin: /target\.com/, credentials:true}));      // substring — loose
```

### The Express greps

```bash
grep -rnoE "cors\(|origin.*:.*true|origin.*function|origin.*=>|origin.*endsWith|origin.*startsWith|origin.*indexOf|origin.*match|origin.*test" <src> | head -20
grep -rnoE "credentials.*:.*true|credentials.*:.*True|allowedHeaders|methods.*:.*'\*'" <src> | head -10
```

### The Express decision-table

```text
cors()                          → `*` — public
origin:true + credentials:true  → reflect+creds — VULN
origin:<allowlist> + credentials → fixed — closed unless bypass
origin:<function> + credentials  → read the function — the check's shape
origin:<regex> + credentials     → the regex's loose-match
no cors() + no ACAO              → not CORS — a different class
```

---

## Flask + flask-cors — the Python canonical

### The default — `CORS(app)` — public `*`

```python
from flask_cors import CORS
CORS(app)   # ACAO: * on all routes — public
```

### The vuln — origins + supports_credentials

```python
CORS(app, origins=['*'], supports_credentials=True)   # *+creds — INVALID combo
CORS(app, origins=True)                                  # reflect-all
CORS(app, origins=r'.*', supports_credentials=True)       # regex reflect-all
CORS(app, origins=['https://*.target.com'])               # subdomain-trust
```

### The per-route config — `@cross_origin()`

```python
from flask_cors import cross_origin
@app.route('/api/me')
@cross_origin(origins='*', supports_credentials=True)   # *+creds — invalid
@cross_origin(origins=True)                                # reflect-all
def me(): ...
```

### The Flask greps

```bash
grep -rnoE 'flask_cors|CORS\(|cross_origin|origins.*=|supports_credentials|allow_headers|methods.*=' <src> | head -20
grep -rnoE '@app\.route|@cross_origin|Access-Control|after_request' <src> | head -20
```

### The hand-rolled Flask CORS — `after_request`

```python
@app.after_request
def add_cors(r):
    r.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin','*')
    r.headers['Access-Control-Allow-Credentials'] = 'true'
    return r
```

A literal reflect — the common hand-rolled vuln.

---

## Django + django-cors-headers — the settings-driven case

```python
# settings.py
INSTALLED_APPS = [..., 'corsheaders', ...]
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', ...]

# the postures:
CORS_ALLOW_ALL_ORIGINS = True                 # reflect-all
CORS_ALLOW_CREDENTIALS = True                  # + all = reflect+creds — VULN
CORS_ALLOWED_ORIGINS = ['https://app.t.com']   # allowlist — closed
CORS_ALLOWED_ORIGINS = ['https://*.t.com']      # subdomain-trust
CORS_ALLOWED_ORIGIN_REGEXES = [r'.*']           # regex reflect-all
CORS_ORIGIN_WHITELIST = [...]                   # the older name
CORS_ALLOW_ALL_ORIGINS + CORS_ALLOW_CREDENTIALS # THE vuln combo
```

```bash
grep -rnoE 'CORS_|corsheaders|CorsMiddleware' <src> | head -20
```

---

## Go — `rs/cors` and hand-rolled

### The `rs/cors` middleware

```go
import "github.com/rs/cors"
c := cors.New(cors.Options{
    AllowedOrigins:   []string{"*"},          // * — public
    AllowCredentials: true,                    // *+creds — invalid
    AllowedOrigins:   []string{"https://*.t.com"}, // subdomain
    AllowOriginFunc:  func(o string) bool { return true }, // reflect-all
})
```

### The hand-rolled Go CORS — the common vuln

```go
// a reflect — the request's Origin echoed
w.Header().Set("Access-Control-Allow-Origin", r.Header.Get("Origin"))
w.Header().Set("Access-Control-Allow-Credentials", "true")

// an OPTIONS handler
if r.Method == "OPTIONS" {
    w.Header().Set("Access-Control-Allow-Methods","GET,POST,PUT")
    w.Header().Set("Access-Control-Allow-Headers","*")
    return
}
```

```bash
grep -rnoE 'rs/cors|cors\.|Access-Control|AllowedOrigins|AllowCredentials|Header().Set.*Origin|OPTIONS' <src> | head -20
```

---

## Spring — `@CrossOrigin` and `WebMvcConfigurer`

```java
// per-controller
@CrossOrigin(origins="*", maxAge=3600)                  // * — public
@CrossOrigin(origins="*",allowCredentials="true")        // *+creds — invalid
@CrossOrigin(origins="https://*.t.com")                  // subdomain
// global
@Override public void addCorsMappings(CorsRegistry r){
  r.addMapping("/**")
   .allowedOriginPatterns("*")                            // patterns — reflect-all
   .allowCredentials(true);                               // + creds — VULN
  r.addMapping("/**")
   .allowedOrigins("https://app.t.com");                   // allowlist — closed
}
```

```bash
grep -rnoE 'CrossOrigin|allowedOrigin|allowCredentials|CorsConfiguration|addCorsMappings|allowedOriginPatterns' <src> | head -20
```

---

## Rails + rack-cors

```ruby
# config/application.rb
Rails.application.config.middleware.insert_before 0, Rack::Cors do
  allow do
    origins '*'                                  # * — public
    origins '*' ; resource '*', credentials: true # *+creds — invalid
    origins [/\.t\.com$/]                         # subdomain-trust
    origins ->(o){o}                              # reflect-all lambda
    resource '*', headers: :any, methods: :any, credentials: true
  end
end
```

```bash
grep -rnoE 'rack-cors|Rack::Cors|origins|resource.*headers|credentials' <src> | head -20
```

---

## Laravel — fruitcake/hand-rolled

```php
// config/cors.php
'allowed_origins' => ['*'],                   // * — public
'allowed_origins' => ['https://*.t.com'],      // subdomain
'allowed_origins_patterns' => ['/.*/'],         // regex reflect-all
'supports_credentials' => true,                // + reflect — VULN
// hand-rolled middleware
$response->headers->set('Access-Control-Allow-Origin', $request->header('Origin'));
$response->headers->set('Access-Control-Allow-Credentials','true');
```

```bash
grep -rnoE 'allowed_origins|supports_credentials|fruitcake|Access-Control|cors\.php|HandleCors' <src> | head -20
```

---

## ASP.NET — `AddCors` policy

```csharp
services.AddCors(o=>o.AddPolicy("p",b=>
  b.AllowAnyOrigin()                            // * — public
   .AllowAnyOrigin().AllowCredentials()          // *+creds — invalid
   .WithOrigins("https://app.t.com")             // allowlist — closed
   .WithOrigins("https://*.t.com")               // subdomain
   .SetIsOriginAllowed(o=>true)                  // reflect-all
   .AllowCredentials()                            // + reflect — VULN
));
```

```bash
grep -rnoE 'AddCors|AllowAnyOrigin|WithOrigins|AllowCredentials|SetIsOriginAllowed|UseCors' <src> | head -20
```

---

## FastAPI/Starlette — `CORSMiddleware`

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware,
  allow_origins=['*'],                           # * — public
  allow_origins=['*'], allow_credentials=True,    # *+creds — invalid
  allow_origins=['https://*.t.com'],              # subdomain
  allow_origin_regex='.*',                         # regex reflect-all
  allow_credentials=True)                          # + regex — VULN
```

```bash
grep -rnoE 'CORSMiddleware|allow_origins|allow_origin_regex|allow_credentials|add_middleware' <src> | head -20
```

---

## Tornado / aiohttp — hand-rolled

```python
# tornado — no built-in CORS
class H(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin",
                        self.request.headers.get("Origin",""))  # REFLECT
        self.set_header("Access-Control-Allow-Credentials","true")
    def options(self):  # the preflight handler
        self.set_header("Access-Control-Allow-Methods","GET,POST")
        self.set_header("Access-Control-Allow-Headers","*")
```

```bash
grep -rnoE 'Access-Control|set_header.*Origin|set_default_headers|def options|aiohttp.*cors|CorsViewAllowables' <src> | head -20
```

---

## nginx/Apache — the proxy-layer CORS

```nginx
# nginx — a reflect at the proxy
add_header Access-Control-Allow-Origin $http_origin;
add_header Access-Control-Allow-Credentials true;
# a map-based allowlist
map $http_origin $cors { default ""; "~*^https://.*\.t\.com$" $http_origin; }
add_header Access-Control-Allow-Origin $cors;
```

```apache
# apache — a reflect
Header set Access-Control-Allow-Origin "%{HTTP_ORIGIN}e"
Header set Access-Control-Allow-Credentials "true"
```

```bash
grep -rnoiE 'add_header|Header.*Access-Control|http_origin|map.*origin|Access-Control' <src>/*.conf <src>/nginx* 2>/dev/null | head -20
```

## The per-stack vuln-table — the condensed matrix

```text
stack           vuln shape                                     grep
Express         cors({origin:true,credentials:true})           origin:true
Flask           CORS(origins=True|r'.*',supports_credentials)   origins
Django          CORS_ALLOW_ALL + CORS_ALLOW_CREDENTIALS         CORS_
Go              Set(A-C-A-Origin, Request.Origin)               Access-Control
Spring          allowedOriginPatterns(*) + allowCredentials     allowedOriginPatterns
Rails           origins ->(o){o} + credentials                  origins.*lambda
Laravel         allowed_origins_patterns.* + supports_cred      allowed_origins
ASP.NET         SetIsOriginAllowed(o=>true) + credentials       SetIsOriginAllowed
FastAPI         allow_origin_regex + allow_credentials          allow_origin_regex
Tornado         set_header(A-C-A-Origin, Request.Origin)        set_header.*Origin
nginx           add_header A-C-A-Origin $http_origin            add_header.*Origin
```
