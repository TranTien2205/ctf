# Detection workflow — the decision procedure from a signal to a verdict

## The entry — a signal that MIGHT be a redirect surface

```text
the signal: a `?next=`/`?url=`/`?redirect=` param on a redirect-prone
            endpoint — OR a `Location:` in a response — OR a meta-refresh
            in the HTML — OR a `location.*` in the bundle
```

## Step 1 — the carrier check

```bash
# is the param a redirect-param? send a known-safe relative + a canary
curl -si "$BASE/x?next=/dashboard" | grep -i '^location'    # the relative baseline
curl -si "$BASE/x?next=https%3A%2F%2Fattacker.invalid" | grep -i '^location'  # the canary
```

```text
Location: /dashboard on the relative   -> the param IS a redirect carrier
Location: <the-canary> on the canary   -> CANDIDATE
Location: / on the canary              -> a safe arm — the fingerprint
no Location on either                  -> a weak-negative — not a carrier
```

## Step 2 — the fingerprint → the filter shape

```text
Location: <canary>        -> no filter — CANDIDATE
Location: /               -> a forced-relative — the /-check
Location: <allowlisted>   -> a host-allowlist — the substring/@/subdomain arms
Location: <partial>       -> a path/host-force — the suffix/substring arms
```

## Step 3 — the arm selection

```text
the filter shape -> the arm family:
  forced-relative   -> the //, /\, \\, %5c, %2f arms
  host-allowlist    -> the @, \@, subdomain, substring, encoded-host arms
  path-force        -> the suffix/substring/userinfo arms
  scheme-check      -> the javascript:/data:/file:/about: arms
  decode-check      -> the encoded/double-encoded arms
```

## Step 4 — the verdict

```text
an arm -> Location: <canary>      -> CANDIDATE -> post-probe confirms
all arms -> Location: <safe>      -> the class falsifier -> close the surface
```

## Step 5 — the carrier-exhaustion check

```text
the Location-carrier is closed -> check the OTHER carriers:
  the meta-refresh          -> curl -s | grep -i 'refresh'
  the JS-nav                -> curl -s | grep -i 'location'
  the location.hash         -> the bundle's hash-parse
  the Referer-derived       -> -H 'Referer: ...' /back
  the stored-redirect       -> the set-then-fire pair
```

## Step 6 — the chain-route

```text
a confirmed Location: <canary> -> route by the laundered-trust:
  on an allowlisted redirect_uri domain  -> the OAuth chain
  + a fetcher that follows               -> the SSRF chain
  + a javascript:/data: sink             -> the XSS chain
  + a bot that visits                    -> the bot chain
  + the phishing shape                   -> the standalone answer
```

## The decision-tree

```text
signal -> carrier check -> fingerprint -> arms -> verdict
    |         |              |            |        |
    |         |              |            |        + candidate/falsifier/negative
    |         |              |            + the filter-shape family
    |         |              + Location: canary/safe/partial
    |         + Location?/meta?/JS?/Referer?/stored?
    + next?/url?/redirect_uri?/...?
```

## The record at each step

```text
step 1 -> record: the carrier + the param
step 2 -> record: the fingerprint (the filter shape)
step 3 -> record: the arms tried
step 4 -> post-probe: the verdict + the verbatim evidence
step 5 -> record: the carriers swept
step 6 -> post-probe: the chain-impact (evidence-kind impact)
```
