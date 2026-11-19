# Oracle selection — the decision tree for picking the channel

The complete selection logic — which oracle for which surface.

---

## Step 1 — is your JS running?

```text
CLASSIC — the bot visits YOUR URL → your JS runs → a client-side
          measure
SEALED  — no attacker JS anywhere → a declarative (CSS) or server-
          state channel
the deciding question: can ANY origin the bot reaches run one line
of your JS? a 'no' forces the sealed shape.
```

## Step 2 — the classic channel-selection

```text
a per-result iframe        → frames.length — a count oracle
a 200/404 search           → onload/onerror — a hit/miss oracle
a slow-vs-fast path        → performance.now() — a timing oracle
a cached resource          → a cache-probe — a cached-vs-uncached
a visited URL              → :visited — a history read
a redirect                 → window.open — a navigation check
a content-size leak        → scrollHeight — a size oracle
a navigation count         → history.length — a count oracle
a load-duration            → resource-timing — a duration read
a render cost              → DOM-timing — a render oracle
```

## Step 3 — the sealed channel-selection

```text
a secret in an ATTRIBUTE   → a CSS-attribute-selector oracle
a secret in TEXT           → a @font-face unicode-range oracle
a font-src wildcard        → the @font-face exfil
an img-src wildcard        → a bg-image CSS-selector oracle
a redis LRU store          → the LRU-eviction channel
a counter                  → the counter channel
a one-shot token           → the single-use flag
a rate-limit bucket        → the quota channel
a 'last seen' timestamp    → the recency channel
a screenshotting bot       → a DOM-writeback read
an airgapped bot           → a server-state/write-back
```

## Step 4 — the bandwidth-selection — how many visits

```text
a one-bit channel          → N visits for a multi-bit secret
a count oracle             → log2(N) bits — a few visits
a char-set oracle          → a whole set in one visit
a recency channel          → thousands of bits — one visit
a high-bandwidth channel   → a single visit suffices
a low-bandwidth channel    → multiple visits needed
```

## Step 5 — the secret-type selection — the reconstruction

```text
a SORTED secret            → a char-set IS the answer — sort the set
an UNSORTED secret         → an n-gram beam search
a length-unknown secret    → a count oracle first — a length-first read
a position-known secret    → a per-position alphabet probe
```

## Step 6 — the feasibility-selection — the arithmetic

```text
the secret's TTL           → the whole leak+decode+submit fits
the request rate           → the markers fit the rps cap
the channel's bandwidth    → enough bits per visit
the bot's context          → a flag-holder session
the exfil's reach          → a listener, a write-back, or a server-state
```

## Step 7 — the spend-order — the one-shot last

```text
the cheaper channels (a counter, a recency, a CSS oracle) narrow
the answer first — the one-shot token's one bit is spent on the
LAST narrowing, not the first.
```

## The per-surface channel-map — the decision table

```text
surface                              channel
a /report + a URL + JS runs          frames.length / onload / timing
a /report + a URL + JS blocked       CSS-selector oracle / @font-face
a secret in an attribute             CSS-attribute-selector
a secret in text                     @font-face unicode-range
a font-src wildcard                  @font-face exfil
a redis LRU                          LRU-eviction channel
a counter/quota                      counter channel
a one-shot token                     single-use flag
a rate-limit bucket                  quota channel
a 'last seen'                        recency channel
a screenshotting bot                 DOM-writeback
an airgapped bot                     server-state / write-back
a managed-policy bot                 declarative / server-state only
a JSDOM                              DOM / timing / count only
a sorted secret                      char-set → sort → answer
an unsorted secret                   n-gram beam search
a short TTL                          high-bandwidth channel
a rate cap                           smaller marker set / different channel
a per-result iframe                  frames.length
a 200/404 search                     onload/onerror
a slow-vs-fast path                  timing
a cached resource                    cache-probe
a visited URL                        :visited
a redirect                           window.open
a content-size leak                  scrollHeight
a navigation count                   history.length
```

## The falsifier — when no channel works

```text
a sealed shape with NO CSS oracle (no attribute, no font wildcard)
AND NO server-state channel (no redis, no counter, no token, no
rate-limit) → the oracle surface is dead → a different class.

an airgapped bot with NO server-state read → no exfil → a write-back
or a different class.

a JSDOM bot with NO DOM channel → a different class.
```
