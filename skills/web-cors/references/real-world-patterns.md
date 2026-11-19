# Real-world patterns — the CORS misconfigs that recur

The shapes that actually show up in production and CTF — each a
measured pattern, not a theoretical one.

---

## 1. The `origin:true` reflect — the Express mistake

```javascript
app.use(cors({origin:true,credentials:true}))
// 'true' reflects the request's Origin — ANY origin allowed WITH creds
```

The most common misconfig — the dev wanted 'allow my front-end' and
wrote `true` which means 'allow whatever asked'.

## 2. The hand-rolled reflect — a `Set` of the request's Origin

```python
self.set_header("Access-Control-Allow-Origin",
                self.request.headers.get("Origin",""))
self.set_header("Access-Control-Allow-Credentials","true")
```

No middleware — a literal reflect — the same vuln without the
framework's safety.

## 3. The `*` + credentials — the invalid combo

```javascript
app.use(cors({origin:'*',credentials:true}))
```

Looks open; the browser rejects it. a `*` endpoint reads public data
only — NOT the vuln.

## 4. The subdomain-trust — `*.target.com`

```python
CORS(app, origins=['https://*.target.com'])
```

Trusts every subdomain — a subdomain XSS, a takeover, or a CTF-sup
sub reads the credentialed data.

## 5. The `null` allow — a leftover test origin

```python
CORS(app, origins=['null','https://app.target.com'])
```

`'null'` left in from local testing — a data:/sandboxed page passes.

## 6. The regex reflect-all — `.*`

```python
CORS(app, origins=r'.*')
```

A regex matching everything — the reflect-all in disguise.

## 7. The prefix/suffix check — a partial-domain match

```javascript
if(origin.startsWith('https://target.com')) // passes target.com.evil.com
```

A naive string check — the lookalike-origin bypass.

## 8. The environment-split — dev's `*` + prod's allowlist

```javascript
origin: isDev ? '*' : 'https://app.target.com'
```

A `*` shipped to prod by accident, or a different config per env —
the deployed check may differ from the source's intent.

## 9. The proxy-overridden ACAO — the CDN's config

```nginx
add_header Access-Control-Allow-Origin $http_origin;
add_header Access-Control-Allow-Credentials true;
```

The proxy reflects the Origin — the app's own CORS is irrelevant.

## 10. The API-gateway passthrough — a wildcard upstream

```text
an API gateway with a CORS plugin — a `*` or a reflect configured
at the gateway, overriding the app's own (or absent) CORS.
```

## 11. The JSONP-legacy — a callback endpoint left open

```javascript
app.get('/api/data',(req,res)=>{
  res.send(req.query.callback+'('+JSON.stringify(data)+')')
})
```

A JSONP endpoint — a script-tag read with no CORS check — a sibling
vuln on the same data.

## 12. The internal-API CORS — a loopback endpoint

```text
an internal API (127.0.0.1, an internal host) with a reflected CORS —
readable by a browser-side fetch via PNA or a same-origin page — the
'internal' assumption isn't a CORS defense.
```

## 13. The SameSite=None+Secure cookie — the ride that enables it

```text
a modern SameSite=None;Secure cookie — needed for a cross-site
credentialed fetch — and the thing that makes a reflected CORS
exploitable in the first place.
```

## 14. The `Vary: Origin` omission — the cache-poison surface

```text
a reflected ACAO without Vary: Origin — a shared cache serves the
attacker-origin response to every visitor.
```

## 15. The pattern-to-probe table

```text
pattern                      probe
origin:true                  Origin: evil.com → reflected
hand-rolled reflect          Origin: evil.com → reflected
* + credentials              Origin: evil.com → * (invalid)
subdomain-trust              Origin: sub.target.com → allowed
null-allow                   Origin: null → allowed
regex reflect-all            Origin: evil.com → allowed
prefix/suffix                Origin: lookalike → allowed
env-split *                  Origin: evil.com → * (public)
proxy-reflect                Origin: evil.com → reflected
JSONP                        ?callback=x → x({...})
```
