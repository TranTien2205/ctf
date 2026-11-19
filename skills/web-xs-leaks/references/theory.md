# Theory — why XS-leaks exist and why they break

The same-origin policy's side-channel leak — the response is opaque
but the browser still leaks its shape.

---

## 1. The problem XS-leaks exploit

```text
the same-origin policy stops a page on origin A from READING a
response from origin B. but the browser still LOADS the response —
frames it, caches it, times it, errors on it — and each of those
observable behaviors differs with the response's content. the
response is opaque; its SIDE EFFECTS are readable.
```

## 2. The side-channel taxonomy — what leaks

```text
a COUNT        — window.frames.length — how many subresources
an EVENT       — onload vs onerror — did the load succeed
a TIME         — performance.now() — how long the response took
a STATE        — a cache, a history, a counter — did it change
a RENDER       — a CSS selector match — did a rule fire
a SERVER-STATE — a mutation the GET caused — readable later
```

## 3. Why the response can't be read but its shape can

```text
SOP gates the RESPONSE BODY — the bytes. it doesn't gate:
- how many <iframe> a page renders (frames.length is readable)
- whether a subresource load errors (onload/onerror fire)
- how long a load takes (performance timing)
- whether a URL is in history (:visited styling)
- whether a resource is cached (a cache-probe timing)
each is a 1-bit-or-more leak per load.
```

## 4. The classic-vs-sealed split — where your code runs

```text
CLASSIC — your page runs on YOUR origin → your JS measures the
side-channel directly — frames.length, onerror, timing, cache.

SEALED — no attacker JS anywhere → the oracle must be DECLARATIVE
(a CSS selector → a resource load) or SERVER-SIDE (a mutation the
GET caused that you read back).

the deciding question: can ANY origin the bot reaches run your JS?
```

## 5. Why a CSS selector reads an attribute

```text
a CSS attribute selector (body[secret^="ab"]) matches a reflected
secret's attribute — a DECLARATIVE match that needs no JS. a
matching rule can set a custom property; an element consuming
thousands of them as background layers fetches exactly the
matched URLs — the requested URLs ARE the matched selectors.
```

## 6. Why @font-face leaks a character-set

```text
a font-face's unicode-range declares which characters it covers —
the browser downloads the face ONLY when a char inside the range
renders. one @font-face per alphabet char + a shared family +
the secret's element = the requested font URLs ARE the character
set of the rendered text.
```

## 7. Why a sorted secret is cheap

```text
a secret built by 'take N random chars, sort them' is fully
determined by its character SET — a char-set oracle returns the
answer directly. an UNSORTED secret needs an n-gram/beam
reconstruction — the set alone doesn't order it.
```

## 8. Why the LRU-eviction channel is high-bandwidth

```text
a store with --maxmemory-policy allkeys-lru evicts the least-
recently-used key on a write. a GET that touches a key REFRESHES
it — marking it recently-used. flood the store → the keys that
survive are the recently-touched ones — the bot's GETs — a
thousand-bit-per-visit channel.
```

## 9. Why the control pair is mandatory

```text
a side-channel is NOISY — a failed run and a negative answer look
identical. the always-true control proves the channel works; the
never-true control proves the measurement isn't ambient noise.
without both, a 'no signal' is uninterpretable.
```

## 10. Why SameSite doesn't save a sealed design

```text
SameSite=Lax/Strict gates CROSS-SITE requests — but a bot's request
to the target itself is same-SITE — the cookie attaches. a sealed
design where the bot only ever visits the target is unaffected by
SameSite — the cookie always rides.
```

## 11. Why the response's shape is the leak

```text
the leak isn't 'what the response says' — it's 'how the browser
behaved loading it'. a page that renders one frame per result
leaks the count; a search that 404s on a miss leaks the miss; a
CSS selector that matches a reflected attribute leaks the match.
the RESPONSE IS OPAQUE; the BEHAVIOR IS THE ORACLE.
```

## 12. The information-theoretic bound — bits per visit

```text
each observable carries log2(possible-states) bits:
- a boolean (hit/miss) = 1 bit
- a count (0..N) = log2(N) bits
- a char-set (subset of 62) = a character-SET (not bits — the whole set)
- a recency channel = thousands of bits (which keys survive)
the channel's bandwidth = bits-per-visit × visits — the feasibility
arithmetic for the whole secret.
```
