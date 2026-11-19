# Per-check (deep) — each verification check's full protocol

## Check: noise baseline

```bash
curl -s -X POST -d "user=$FAKE&pass=x" "$BASE/<f>" -o b1
curl -s -X POST -d "user=$FAKE&pass=x" "$BASE/<f>" -o b2
diff b1 b2   # the varying lines = the per-request noise
```

Pass: noise identified (CSRF/timestamp/nonce/request-id) and masked.
Fail-to-mask: re-fetch a fresh token per request; if every byte still
differs, the response is per-request-unique — use the status/timing
channel.

## Check: masked body

```bash
mask() { sed -E 's/(csrf|nonce|token|_ts|request_id|timestamp)[^<"& ]*//g;s/value="[^"]*"//g;s/[a-zA-Z0-9+/=]{20,}//g'; }
diff <(mask<good) <(mask<bad1)
```

Pass: a surviving difference (an error word/code/class/field) → the
body channel confirms. Fail: masked-identical → closed.

## Check: status + redirect

```bash
for u in "$KNOWN" "$FAKE" "$FAKE"; do
  curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}\n' -X POST -d "user=$u&pass=x" "$BASE/<f>"
done
```

Pass: a differing code or `Location`, identical across the two `FAKE`
reads → confirms. Fail: identical → closed.

## Check: timing

```bash
# N>=8 interleaved, session-pinned
for i in $(seq 10); do
  curl -sb cj -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$KNOWN&pass=x" "$BASE/<f>"
  curl -sb cj -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE&pass=x" "$BASE/<f>"
done
```

Pass: `median(good)-median(bad) > ~3*jitter`, re-run-confirmed → timing
oracle. Fail: sub-jitter → closed.

## Check: envelope

```bash
diff <(curl -sD - -o/dev/null -X POST -d "user=$KNOWN&pass=x" "$BASE/<f>" | grep -iE 'set-cookie|x-|retry|ratelimit') \
     <(curl -sD - -o/dev/null -X POST -d "user=$FAKE&pass=x" "$BASE/<f>" | grep -iE 'set-cookie|x-|retry|ratelimit')
```

Pass: a cookie/header difference → side oracle. Fail: identical → closed.

## Check: send side-effect

```bash
curl -s -X POST -d "email=$KNOWN" "$BASE/reset" | grep -oE '(sent|queued|to|emails)[^,}]*'
curl -s -X POST -d "email=$FAKE"  "$BASE/reset" | grep -oE '(sent|queued|to|emails)[^,}]*'
```

Pass: `{"emails_queued":1}` vs `0`, or a real send only for known → the
send oracle. Fail: identical → closed.

## Check: lockout

```bash
for i in $(seq 1 12); do curl -s -o /dev/null -w '%{http_code} ' -X POST -d "user=$KNOWN&pass=x" "$BASE/login"; done
```

Pass: a `423`/`429` on `KNOWN` but not `FAKE` → the lock oracle + the
threshold. Fail: both lock or neither → closed.
