# Framework matrix — the CORS surface per stack

Each framework's CORS mechanism, its default posture, and the grep
that finds the misconfig.

---

## Express / the `cors` middleware

```javascript
// the defense: cors() middleware
// the holes:
app.use(cors())                          // ACAO:* — open public
app.use(cors({origin:true,credentials:true}))  // REFLECTS the origin
                                             // + credentials — the vuln
app.use(cors({origin:/\.target\.com$/})) // suffix — subdomain-trust
app.use(cors({origin:'*',credentials:true}))   // invalid combo —
                                             // browser rejects
app.use(cors({origin:function(o,cb){cb(null,true)}})) // reflect-all
```

```bash
grep -rn 'cors\|origin\|Access-Control\|allowedOrigins\|credentials' <src> | head -30
```

## Flask / flask-cors

```python
# the defense: flask_cors.CORS
# the holes:
CORS(app)                                   # ACAO:* on all — public
CORS(app,origins='*',supports_credentials=True)  # * + creds — invalid
CORS(app,origins=['https://*.target.com'])  # subdomain-trust
CORS(app,origins=r'.*')                      # a reflect-all regex
CORS(app,origins=True)                       # reflect all
```

```bash
grep -rn 'flask_cors\|CORS(\|origins\|supports_credentials\|Access-Control' <src>
```

## Django / django-cors-headers

```python
# the defense: corsheaders middleware
# the holes:
CORS_ALLOW_ALL_ORIGINS = True                 # reflect-all
CORS_ALLOWED_ORIGINS = ['https://*.target.com']  # subdomain
CORS_ALLOWED_ORIGIN_REGEXES = [r'.*']          # regex — open
CORS_ALLOW_CREDENTIALS = True                  # + reflect-all = vuln
CORS_ORIGIN_WHITELIST — the older name
```

```bash
grep -rn 'CORS_\|corsheaders\|Access-Control' <src>
```

## Go / Gin — hand-rolled or `rs/cors`

```go
// the defense: github.com/rs/cors or hand-rolled
// the holes:
cors.AllowAll()                                // ACAO:* — public
cors.New(cors.Options{AllowedOrigins:[]string{"*"},
    AllowCredentials:true})                    // invalid combo
// hand-rolled reflection — the common vuln:
c.Writer.Header().Set("Access-Control-Allow-Origin",
    c.Request.Header.Get("Origin"))            // REFLECT — the vuln
c.Writer.Header().Set("Access-Control-Allow-Credentials","true")
```

```bash
grep -rn 'cors\|Access-Control\|AllowedOrigins\|Origin' <src>
```

## Rails / rack-cors

```ruby
# the defense: rack-cors middleware
# the holes:
origins '*'                                  # ACAO:* — public
origins '*' ; resource '*', headers: :any, methods: :any,
  credentials: true                          # * + creds — invalid
origins [/\.target\.com$/]                   # suffix — subdomain-trust
origins ->(o){o}                             # reflect-all lambda
```

```bash
grep -rn 'rack-cors\|origins\|Access-Control\|credentials' <src>
```

## Spring — the @CrossOrigin / WebMvcConfigurer

```java
// the defense: @CrossOrigin or a global config
// the holes:
@CrossOrigin(origins="*",allowCredentials="true")   // invalid combo
@CrossOrigin(origins="https://*.target.com")        // subdomain
registry.addMapping("/**").allowedOriginPatterns("*") // patterns — open
    .allowCredentials(true)                           // + creds — vuln
.allowedOrigins("*")                                   // * — public
```

```bash
grep -rn 'CrossOrigin\|allowedOrigin\|allowCredentials\|CorsConfiguration' <src>
```

## Laravel — the global middleware / fruitcake

```php
// the defense: a CORS middleware
// the holes:
'allowed_origins' => ['*'],                  // * — public
'allowed_origins_patterns' => ['/.*/'],       // reflect-all
'supports_credentials' => true,               // + reflect — vuln
// hand-rolled:
header('Access-Control-Allow-Origin: '.$_SERVER['HTTP_ORIGIN']);  // reflect
```

```bash
grep -rn 'allowed_origins\|supports_credentials\|Access-Control\|fruitcake\|cors' <src>
```

## ASP.NET — the CORS policy

```csharp
// the defense: AddCors policy
// the holes:
.AllowAnyOrigin()                            // * — public
.AllowAnyOrigin().AllowCredentials()         // invalid combo
.WithOrigins("*").AllowCredentials()         // same
.SetIsOriginAllowed(o=>true)                 // reflect-all
.WithOrigins("https://*.target.com")         // subdomain-trust
```

## FastAPI / Starlette — the CORSMiddleware

```python
# the defense: CORSMiddleware
# the holes:
allow_origins=['*'],allow_credentials=True   # invalid combo
allow_origins=['*']                           # * — public
allow_origin_regex='.*'                       # reflect-all
allow_origins=['https://*.target.com']        # subdomain
```

## Tornado / aiohttp — hand-rolled

```python
# no built-in CORS — a hand-rolled set of headers
self.set_header("Access-Control-Allow-Origin",
                self.request.headers.get("Origin",""))   # reflect
self.set_header("Access-Control-Allow-Credentials","true")
```

## The per-framework grep — the posture in one pass

```bash
grep -rnoiE 'cors|Access-Control|allow_origins|allowed_origins|origins|credentials|allowedOrigin|CrossOrigin|cors\(\)|CORSMiddleware|flask_cors|rack-cors|django-cors-headers|SupportsCredentials|allowedOriginPatterns|allow_origin_regex' \
  <src> | head -40
```

## The per-framework vuln-table

| Framework | The vuln shape |
|---|---|
| Express | `cors({origin:true,credentials:true})` — reflect+creds |
| Flask | `CORS(origins=True,supports_credentials=True)` |
| Django | `CORS_ALLOW_ALL_ORIGINS + CORS_ALLOW_CREDENTIALS` |
| Go | a hand-rolled `Set(A-C-A-Origin, Request.Origin)` |
| Rails | `origins ->(o){o}` + `credentials: true` |
| Spring | `allowedOriginPatterns("*")` + `allowCredentials` |
| Laravel | `allowed_origins_patterns.*` + `supports_credentials` |
| ASP.NET | `SetIsOriginAllowed(o=>true)` + credentials |
| FastAPI | `allow_origin_regex='.*'` + `allow_credentials` |
| hand-rolled | a literal reflect of the request's Origin + ACAC |

## The falsifier

```text
a strict allowlist (exact-match origins, no wildcard/regex/
subdomain/reflect) + no ACAC — the read is closed.
```
