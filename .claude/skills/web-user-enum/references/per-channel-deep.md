# Per-channel (deep) — each channel's exhaustive protocol

## Body channel — the exhaustive diff

```bash
# 1. raw byte diff
cmp -l good bad1 | head
# 2. length delta
wc -c good bad1
# 3. whitespace-normalized
diff <(tr -s ' \t\n' ' ' <good) <(tr -s ' \t\n' ' ' <bad1)
# 4. noise-masked
mask() { sed -E 's/(csrf|nonce|token|_ts|request_id|timestamp)[^<"& ]*//g;s/value="[^"]*"//g;s/[a-zA-Z0-9+/=]{20,}//g'; }
diff <(mask<good) <(mask<bad1)
# 5. extract just the error block
grep -oE '<(div|span|p|li|small|td)[^>]*(error|alert|invalid|fail|denied|wrong|exist|found)[^>]*>[^<]*' good bad1
# 6. JSON field diff (API)
python3 -c "import json;print(set(json.load(open('good')).items())^set(json.load(open('bad1')).items()))"
```

## Status + redirect channel — exhaustive

```bash
# the full status line + Location + any query param
curl -s -D - -o /dev/null -X POST -d "user=$KNOWN&pass=x" "$BASE/<f>" | grep -iE '^HTTP|^location'
curl -s -D - -o /dev/null -X POST -d "user=$FAKE&pass=x"  "$BASE/<f>" | grep -iE '^HTTP|^location'
# every redirect-param name — ?e= ?error= ?msg= ?reason= ?code= ?status=
```

## Timing channel — exhaustive

```bash
# N=12 interleaved, session-pinned, cache-bust param
> t; for i in $(seq 12); do
  curl -sb cj -o /dev/null -w "g %{time_total}\n" -X POST -d "user=$KNOWN&pass=x&_=$i" "$BASE/<f>" >> t
  curl -sb cj -o /dev/null -w "b %{time_total}\n" -X POST -d "user=$FAKE&pass=x&_=$i"  "$BASE/<f>" >> t
done
python3 -c "
import statistics as s
g=[float(l.split()[1])for l in open('t')if l[0]=='g']
b=[float(l.split()[1])for l in open('t')if l[0]=='b']
print('med',round(s.median(g),3),round(s.median(b),3),'delta',round(s.median(g)-s.median(b),3),
      'stdev',round(s.stdev(g),3),round(s.stdev(b),3),'jitter',round(s.stdev(g+b),3))
"
# variance oracle: stdev(g) vs stdev(b) — a fixed dummy-hash is tighter
```

## Side-artifact channel — exhaustive

```bash
# the FULL envelope — every header, every cookie
curl -sv -X POST -d "user=$KNOWN&pass=x" "$BASE/<f>" 2>&1 | grep -iE '^< |set-cookie' > g.env
curl -sv -X POST -d "user=$FAKE&pass=x"  "$BASE/<f>" 2>&1 | grep -iE '^< |set-cookie' > b.env
diff g.env b.env
# the send side-effect
curl -s -X POST -d "email=$KNOWN" "$BASE/reset" | grep -oE '(sent|queued|emails|to)[^,}]*'
curl -s -X POST -d "email=$FAKE"  "$BASE/reset" | grep -oE '(sent|queued|emails|to)[^,}]*'
# the lock artifact
for i in $(seq 12); do curl -s -o /dev/null -w '%{http_code} ' -X POST -d "user=$KNOWN&pass=x" "$BASE/login"; done
```

Each channel is closed only when its EXHAUSTIVE read is uniform across
the repeated-bad pair and a second bad name.
