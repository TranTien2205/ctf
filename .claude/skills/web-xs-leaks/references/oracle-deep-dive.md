# Oracle deep dive — the remaining channel details

The subtler mechanics and the less-common variants of each oracle.

---

## 1. The frames.length edge — a same-origin vs cross-origin read

```text
window.frames.length is readable cross-origin — the COUNT, not the
content. a same-origin iframe's frames.length is the same property —
the difference: a same-origin read also reads the frame's DOM; a
cross-origin read reads only the count.
```

## 2. The onload/onerror edge — a per-element-type read

```text
an <img>/<script>/<link>/<iframe>/<video>/<audio>/<object> all fire
onload/onerror — the event is a browser-side signal. the per-type
difference: an <img> fires on a 200 or a 404's content-type; a
<script> fires on a parseable-or-not — the events are the same
oracle with a different trigger.
```

## 3. The timing-oracle edge — the noise floor

```text
a timing channel's noise floor is the server's jitter + the network's
latency + the scheduler's quantum — the threshold sits in the noise.
fix: average over N samples — the mean's variance shrinks as 1/N —
a threshold between the slow and fast means separates the states.
```

## 4. The cache-probe edge — the partition's limit

```text
a partitioned cache (per top-frame site) — a resource cached on site
A isn't shared with site B — the probe reads 'was it cached on THIS
site' — a same-site or a same-partition read. a cross-site cache-
probe is dead.
```

## 5. The :visited edge — the render-side-channel

```text
a computed-style query returns the UNVISITED style (a privacy
partition) — the :visited channel is a RENDER-side-channel — a
repaint cost or a font-load trigger on a :visited selector — not a
computed-style read.
```

## 6. The CSS-selector edge — the attribute-vs-text requirement

```text
an attribute-selector needs the secret IN an attribute — a secret
in TEXT content doesn't match — a unicode-range @font-face reads
the rendered text, not an attribute.
```

## 7. The @font-face edge — the font-src wildcard requirement

```text
a font-src wildcard ('self' *) allows the external font host — the
@font-face unicode-range channel's exfil — 'font-src self' (no
wildcard) blocks it — check WHICH directive has the hole.
```

## 8. The LRU edge — the blast radius

```text
an LRU flood evicts EVERY other key — possibly the secret itself —
the blast_radius — only flood an instance that's yours alone — a
shared-store flood is a destructive channel.
```

## 9. The one-shot-token edge — the spend-last ordering

```text
a GETDEL's 'did it survive' burns the check — a spent token is gone —
spend it LAST — the cheaper channels (a counter, a recency, a CSS
oracle) narrow the answer first.
```

## 10. The meta-refresh edge — the same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — it
carries the Lax cookie — the sealed shape's whole design exploits
this — the bot's privileged request is a same-site navigation.
```

## 11. The write-back edge — the target's storage

```text
a write-back lands the data on the TARGET — a comment, a field, a
stored value — you read it back via a GET — an airgapped exfil.
```

## 12. The DOM-writeback edge — the screenshot read

```text
a bot that screenshots the page — a DOM-writeback (the secret
rendered visibly) — the screenshot IS the exfil — no listener
needed.
```

## 13. The DNS-exfil edge — the subdomain carrier

```text
a DNS lookup carries the data in the subdomain — an airgapped case
where the bot can resolve DNS but not reach your listener directly.
```

## 14. The postMessage edge — a real read primitive

```text
a postMessage '*' broadcast transmits the data — a real read
primitive (a broadcast, not a measure) — the data is sent, not
inferred — a different class boundary.
```

## 15. The sorted-secret edge — the set IS the answer

```text
'take N random chars, sort them' — the ordering is KNOWN — the set
IS the string — a char-set oracle returns the answer directly.
```

## 16. The unsorted-secret edge — the n-gram reconstruction

```text
an unsorted secret's set doesn't order it — an n-gram/beam
reconstruction is required — a set of overlapping substrings
stitches into the secret.
```
