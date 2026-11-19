# Per-vector (deep) — every input vector's full protocol

## The field-name vectors — probe each

```bash
for field in user username email login account name uid uname user_name \
             login_id handle member sub principal identifier phone mobile; do
  printf '%-12s ' "$field"
  curl -s -o /dev/null -w '%{http_code}' -X POST -d "$field=$KNOWN&pass=x" "$BASE/login"
  printf '  '
  curl -s -o /dev/null -w '%{http_code}\n' -X POST -d "$field=$FAKE&pass=x" "$BASE/login"
done
```

The app reads ONE of these as the username slot — the field that
produces a differential is the live slot. A `400`/`422` on the wrong
field is a missing-param, not an oracle.

## The format vectors — within the slot

```bash
for u in 'admin' 'admin@corp.com' 'ADMIN' 'Admin' 'corp\admin' \
         'admin.corp' 'a.admin' 'admin_x' 'admin\x00' ' admin '; do
  printf '%-18s ' "$u"; curl -s -o /dev/null -w '%{http_code}\n' \
    -X POST -d "user=$u&pass=x" "$BASE/login"
done
```

A `404`/`400` on `admin@x.c` that `admin` does not trigger is a FORMAT
error — resolve the format before reading the oracle.

## The transport vectors

```bash
# form-encoded
curl -X POST -d "user=$U&pass=x" "$BASE/login"
# JSON
curl -X POST -H 'Content-Type: application/json' -d "{\"username\":\"$U\",\"password\":\"x\"}" "$BASE/api/login"
# GET query
curl "$BASE/check?user=$U"
# basic-auth
curl -u "$U:x" "$BASE/protected"
# GraphQL
curl -X POST -d "{\"query\":\"mutation{login(username:\\\"$U\\\",password:\\\"x\\\"){token}}\"}" "$BASE/graphql"
# websocket auth frame
echo '{"type":"auth","user":"'$U'","pass":"x"}' | websocat "$WS"
```

## The multi-field vectors

Some forms check the username AND the email — probe each independently:

```bash
curl -d "user=AAA&email=SAME@x.c" "$BASE/register"   # vary user, hold email
curl -d "user=SAME&email=a@x.c"  "$BASE/register"   # vary email, hold user
```

## The vector-to-oracle note

The vector is the TRANSPORT for `{U}` — the oracle measurement is the
same three arms on the same channel, whatever the field/format/
transport. A vector that produces a differential is the live slot;
the channel files carry the measurement.
