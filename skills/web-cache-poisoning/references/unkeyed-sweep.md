# Unkeyed sweep — the unkeyed-input sweep, in one place

The complete unkeyed-input sweep — the dictionary, the check, the falsifier.

---

## 1. The sweep — every candidate input

```bash
# for each candidate input — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'X-Rewrite-URL' 'X-Forwarded-Scheme' 'X-Forwarded-Proto' 'X-Host' 'X-Forwarded-Server' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'Accept-Encoding' 'Accept' 'X-Real-IP' 'X-HTTP-Method-Override' 'X-Forwarded-Port' 'X-Forwarded-Uri' 'Origin' 'X-Requested-With' 'Forwarded' 'X-Forwarded-Domain' 'X-Forwarded-Ssl' 'X-Forwarded-Email' 'X-Forwarded-User' 'X-Custom' 'X-Debug' 'X-Preview' 'X-Frame-Options'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## 2. The check — the unkeyed confirm

```text
the unkeyed check: send the input → the stored copy serves it to a
clean request → the marker persists into the clean response → unkeyed
→ poisonable.
```

## 3. The per-input surface map — which input for which surface

```text
X-Forwarded-Host        → URL-rewrite (the app's links use YOUR host)
X-Forwarded-Scheme      → scheme-downgrade (the links use http)
X-Original-URL          → path-rewrite (the app serves a different route)
User-Agent              → per-UA response (a mobile-vs-desktop confusion)
Referer                 → reflected input (the page echoes it)
Accept-Language         → localized response (a per-language copy)
Accept-Charset          → charset confusion (a charset injection)
Accept-Encoding         → per-encoding copy (a compression confusion)
Cookie                  → per-session copy (usually keyed via Vary)
X-Forwarded-For         → per-IP copy (usually keyed if read)
X-HTTP-Method-Override  → method-override (a per-method confusion)
```

## 4. The keyed-input falsifier — a per-input entry

```text
a keyed input → a per-input entry → YOUR input's effect is in YOUR
copy only → the clean request doesn't reflect → a different class.
```

## 5. The sweep's falsifier — when nothing is unkeyed

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class. the whole attack depends on a request
part the app reads but the cache ignores — none means a different
class.
```

## 6. The sweep's edge — a Vary'd header

```text
a Vary'd header → a keyed header → a per-input entry → not the
poisoning vector.
```

## 7. The sweep's edge — a MISS reflection

```text
a marker reflected on a MISS → the response came from the origin —
a REFLECTION, not a poisoning — the stored copy didn't serve it.
```

## 8. The sweep's edge — a keyed param

```text
a keyed param → a per-value entry → a cache-buster → a different class.
```
