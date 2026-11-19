# Quick start — the 60-second pass

## The five commands that answer the class

```bash
# 1. the direct oracle — the cheapest check
curl "$BASE/api/username-available?u=admin"          # {"available":false} -> oracle
curl "$BASE/check-username?u=zzz-x"                  # {"available":true}

# 2. the three arms on the login body
curl -i -X POST -d 'user=admin&pass=x' "$BASE/login" > /tmp/g
curl -i -X POST -d 'user=zzz-x&pass=x' "$BASE/login" > /tmp/b
diff /tmp/g /tmp/b                                   # a delta -> oracle

# 3. the timing baseline
for i in $(seq 10); do curl -o /dev/null -w '%{time_total}\n' -d 'user=admin&pass=x' "$BASE/login"; curl -o /dev/null -w '%{time_total}\n' -d 'user=zzz-x&pass=x' "$BASE/login"; done

# 4. the throttle
for i in $(seq 15); do curl -o /dev/null -w '%{http_code} ' -d 'user=x&pass=y' "$BASE/login"; done

# 5. the seeded list through a confirmed oracle
for u in admin service flag backup root; do curl -s "$BASE/api/username-available?u=$u"; done
```

## The one-line mental model

`KNOWN` vs `FAKE` vs `FAKE2` — measure the BODY, the STATUS+`Location`,
the TIMING (N>=8 median), and the SIDE (cookie/send/lock) — on EVERY
account form (login/register/reset/check/api/graphql/users). A repeated
delta on any channel is an oracle; the verified accounts route to
`web-auth-session`/`web-idor`/`web-oauth-sso`.

## The routes

- the full surface: `form-surface-deep.md`, `index.md`
- the channels: `channels.md`, `channel-body/status/side`, `timing-oracle`
- the throttle: `throttling.md`, `rate-limit-bypass.md`, `throttle-taxonomy.md`
- the chains: `exploitation.md`, `multi-step-chains.md`
- the verify: `verification-protocol.md`, `verification-workflow.md`
