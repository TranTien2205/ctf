# Server-state channels — the sealed-shape read-back

When no attacker JS runs, the oracle is a server-side state change
a plain GET can cause — and that you can read afterwards.

---

## 1. The channel classes — what a GET can mutate

```text
a counter that increments            → read the next value
a cache/store recency                → an LRU eviction
a one-shot token consumed by the GET → a single-use flag
a rate-limit bucket                  → a quota counter
a 'last seen' timestamp              → a recency read
a session/state flag                 → a mutated field
```

## 2. The LRU-eviction channel — the highest-bandwidth sealed oracle

```text
a store with an LRU eviction policy (redis --maxmemory-policy
allkeys-lru) — every GET that touches a key refreshes it. after you
FLOOD the store to force eviction, THE KEYS THAT SURVIVE ARE THE
ONES THE VICTIM'S BROWSER FETCHED — thousands of bits per visit.
```

```bash
# the eviction-policy grep
grep -rnoiE 'maxmemory|allkeys|lru|evict|policy|expire|ttl' <src> | head -20
```

## 3. The counter channel — a next-value read

```text
a GET that increments a counter you can read — 'GET /x' sets
counter++ → you read counter's next value → the difference tells
you whether the victim's GET ran.
```

## 4. The one-shot-token channel — a single-use flag

```text
a GETDEL or a single-use nonce — a GET that consumes it — 'did the
token survive' is a one-bit answer. it burns your own ability to
check — spend it last.
```

## 5. The rate-limit/quota channel — a bucket read

```text
a rate-limit bucket or a quota counter that a GET decrements —
the remaining count is a read-back.
```

## 6. The 'last seen' timestamp — a recency read

```text
a 'last seen' / 'last modified' / 'last access' timestamp that a
GET updates — a recency channel.
```

## 7. The channel-discovery greps — finding the mutation surface

```bash
# every GET-reachable mutation — the read-back surface
grep -rnoiE 'incr|counter|count|get|set|lpush|rpush|expire|ttl|GETDEL|rate.?limit|quota|nonce|token|update|last' <src> | head -30

# the store's eviction policy
grep -rnoiE 'maxmemory|allkeys|lru|evict|policy' <src> | head -10

# a counter/state you can read back unauthenticated
grep -rnoiE 'counter|count|next|seq|id.*\+\+|value|state' <src> | head -20
```

## 8. The channel-bandwidth table — how many bits per visit

```text
channel                    bits/visit    note
a one-shot token           1             burns your check — spend last
a counter++                ~log2(range)  a few bits
a recency/LRU              thousands     the keys-that-survive are the leak
a rate-limit bucket        ~log2(bucket) a few bits
a timestamp                ~1-2          a coarse recency
a CSS-oracle               thousands     the matched selectors are the leak
```

## 9. The destructive-channel warning — the flood's blast radius

```text
a flood that forces LRU eviction DESTROYS every other key in the
store — only run it against an instance that's yours alone, and
read the chain card's blast_radius first. the store's OWN keys are
evictable too — you can delete the thing you're trying to read.
```

## 10. The channel-selection — which sealed oracle

```text
a redis/store with LRU        → the eviction channel — high bandwidth
a counter++ endpoint          → the counter channel — a few bits
a one-shot token              → the single-use flag — one bit, last
a rate-limit bucket           → the quota channel — a few bits
a 'last seen' field           → the recency channel — a bit or two
none of the above + a CSS oracle → the declarative channel
```
