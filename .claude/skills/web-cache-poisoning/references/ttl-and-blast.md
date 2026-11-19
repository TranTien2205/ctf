# TTL and blast radius — the deception's persistence and scope

How long a poisoned entry lives, and how many requesters it affects.

---

## 1. The stored copy's TTL — the deception's persistence

```text
a stored entry lives until its TTL — the deception persists for the
TTL — a short TTL is a short-lived deception; a long TTL is a
persistent one.
```

```bash
# the stored copy's TTL — the max-age + the Age
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'cache-control|age:|expires'
#   Cache-Control: max-age=300 → a 5-minute TTL
#   Age: 120 → the copy is 120s old — 180s remain
```

## 2. The blast radius — the URL's requester base

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast radius is the URL's requester base —
a public URL poisons every visitor.
```

```text
a shared URL (a public page) → every requester gets the poisoned copy.
a rare URL (a probe with a cachebuster) → only requests for that key.
```

## 3. The TTL's origin — where the TTL comes from

```text
the TTL comes from the response's cache-control/expires or the
proxy's proxy_cache_valid config — the stored copy's lifetime is
min(the response's max-age, the proxy's TTL).
```

```nginx
# a typical nginx config — the default TTL
proxy_cache_valid 200 60m;     # a 60-minute TTL for 200s
proxy_cache_valid 404 1m;      # a 1-minute TTL for 404s
```

## 4. The TTL measurement — how long the deception lives

```bash
# measure the TTL — the Age growth over time
curl -sI "$BASE/page?cb=<unique>" | grep -i 'age:'
#   Age: 30 → the copy is 30s old — wait + re-check to see the expiry
sleep 60 && curl -sI "$BASE/page?cb=<unique>" | grep -i 'age:'
#   Age resets or the copy expires → the TTL
```

## 5. The deception's window — the TTL's attack surface

```text
a short TTL → a short deception window → a probe that expires before
a bot views it.
a long TTL → a persistent deception → a poisoned page that stays.
a measured TTL → the window for the bot/viewer's visit.
```

## 6. The shared-store safety — the blast-radius discipline

```text
a poisoned entry is shared — the deception affects EVERY requester
of the URL — a real-world blast radius. in a CTF:
- use a harmless marker — no destructive payload on a shared store
- use a cachebuster — a unique key per probe — a confined blast
- clean up — the poisoned entry expires, but a long TTL persists
- keep the window short — a short-TTL URL, a quick confirm
```

## 7. The cachebuster confinement — a probe-only blast

```bash
# a cachebuster — a unique key per probe — a confined blast
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # stored under /page?cb=<unique>
curl "$BASE/page?cb=<unique>"   # only requests for this key get the poisoned copy
```

```text
a cachebuster confines the blast — only requests for YOUR unique key
get the poisoned copy — the rest of the URL's requesters get a clean
copy.
```

## 8. The public-URL blast — an unconstrained deception

```text
a public URL (a real page the app's visitors request) — a poisoned
copy reaches EVERY visitor — a real-world blast radius. the verified
card's shape: an authenticated page cached under a shared URL — the
stored copy serves the privileged page to anyone.
```

## 9. The TTL's falsifier — a short-lived deception

```text
a short TTL → the deception expires before a bot views it → a
wrong-context case. record it: 'the TTL is <N>s — the deception
persisted only for the window — a short-lived case'.
```

## 10. The per-case blast-map — which blast for which URL

```text
a cachebuster URL    → a confined blast (only your key's requests)
a public URL         → every visitor (a real-world blast)
a rare URL           → a small blast (only your key's requests)
a shared URL         → every requester of that URL
```

## 11. The TTL's confirm — the expiry check

```bash
# re-request after the TTL — the stored copy expired?
sleep <TTL> && curl "$BASE/page?cb=<unique>"
#   a fresh fetch (a MISS) → the copy expired
```

## 12. The cleanup — removing the poisoned copy

```bash
# the poisoned entry expires on its TTL — or an explicit purge
# a PURGE request if the proxy accepts it
curl -X PURGE "$BASE/page?cb=<unique>"
# or a cache-buster on a new key — a fresh entry
```

## 13. The TTL's edge — a stale copy

```text
a stale copy — the TTL passed but the proxy served the old copy —
the deception persists past the TTL — a stale-while-revalidate or
a proxy that serves stale on error.
```
