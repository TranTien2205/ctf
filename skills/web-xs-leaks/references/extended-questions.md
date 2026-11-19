# Extended questions — the deeper XS-leak confusions

The subtler questions that come up in a real engagement.

---

## Q: the bot runs my JS — but can it read the target's response?

No — your page runs on YOUR origin — a fetch to the target returns
an OPAQUE response (no ACAO). your JS can't read the body — it can
only MEASURE the response's shape (a frame-count, an error, a
timing, a CSS match). that's the whole XS-leak.

## Q: a `no-cors` fetch — does the cookie ride?

a `no-cors` fetch carries the cookie only if SameSite allows it —
a Lax cookie doesn't ride a cross-site fetch; a None+Secure does.
the response is opaque either way — the cookie question is about
the FETCH's credential, not the read.

## Q: a frame-count oracle — is it really cross-origin readable?

yes — `iframe.contentWindow.frames.length` is readable cross-origin
(the count, not the content). a per-result iframe count is a count
oracle — the classic XS-leak shape.

## Q: a :visited read — why doesn't `getComputedStyle` work?

modern browsers partition :visited per top-frame site — a computed-
style query returns the unvisited style — the channel is a RENDER-
side-channel (a repaint cost, a font-load trigger on a :visited
selector), not a computed-style read.

## Q: a cache-probe — why is it same-site only?

a partitioned cache (per top-frame site) — a resource cached on
site A isn't shared with site B — the cache-probe reads 'was it
cached on THIS site' — a same-site or a same-partition read.

## Q: a sorted secret — why is the char-set the answer?

'take N random chars, sort them' — the ordering is KNOWN (sorted) —
the character-set fully determines the string. sort the leaked set
→ the token. no ordering work needed — the set IS the answer.

## Q: an unsorted secret — why does it need a beam search?

the char-set doesn't order it — a set of n-grams (each a substring
the channel confirmed) stitches into the secret — a beam search
keeps the top-W candidates at each extension — a noise-aware
reconstruction.

## Q: a substring oracle — why thousands of rules?

a 'does X occur' oracle needs one rule per n-gram — a 62-char
alphabet's 2-grams = 3844 rules; 3-grams = 238328 — the CSS engine
evaluates them all declaratively — the matched set is the n-gram
coverage the beam search stitches.

## Q: a font-src wildcard — why is it the exfil?

'font-src self *' — a host wildcard on fonts — an external font
host is allowed — one @font-face per alphabet char + a unicode-range
= the requested font URLs ARE the character-set — the font host IS
the exfil listener.

## Q: a meta-refresh — why does it bypass SameSite?

a meta-refresh issued BY THE TARGET is a same-site navigation — the
browser treats it as a top-level navigation on the same site — the
Lax cookie rides. the sealed shape's whole design exploits this —
the bot's privileged request is a same-site navigation.

## Q: an LRU flood — why is it destructive?

`--maxmemory-policy allkeys-lru` — every write can evict the least-
recently-used key — a flood that forces eviction destroys EVERY
other key — possibly the secret itself. only flood an instance
that's yours alone — read the blast_radius.

## Q: a one-shot token — why spend it last?

a GETDEL's 'did it survive' is one bit AND burns the check — a
spent token is gone. the cheaper channels (a counter, a recency, a
CSS oracle) narrow the answer first — the one-shot's one bit is
spent on the LAST narrowing, not the first.

## Q: a JSDOM bot — why are the CSS channels dead?

JSDOM has no rendering engine — no CSS layout, no font matching, no
:visited styling — the visual/CSS channels are dead. only the DOM
channels (frames.length, a count, a timing) survive.

## Q: a managed-policy bot — why is the sealed shape forced?

URLBlocklist ['*'] + URLAllowlist — the bot can ONLY visit the
target's origin — NO attacker URL reaches it — no attacker JS, no
attacker CSS — only a declarative or server-state channel works.

## Q: a write-back — why is it an airgapped exfil?

an airgapped bot can't reach your listener — a write-back (a POST
to the target storing the leaked data — a comment, a field) lands
the data on the TARGET — you read it back later — no external
listener needed.

## Q: a DOM-writeback — when does it work?

a bot that SCREENSHOTS the page — a DOM-writeback (the secret
rendered visibly in a large font) — the screenshot IS the exfil —
no listener, no server-state read needed.

## Q: a count oracle — why is it more than one bit?

frames.length is a COUNT (0..N) — log2(N) bits per load — a 'how
many results' read is more than a hit/miss — it narrows the
secret's length before the char-by-char.

## Q: the sealed shape — why does the cookie ride?

the bot's request to the target ITSELF is same-SITE — the Lax
cookie rides on a same-site request — the cross-site cookie
question only matters in the CLASSIC shape (a cross-site fetch).

## Q: a noisy channel — how do I get a clean read?

average over N samples (a timing oracle), a control pair (to
separate signal from noise), or a higher-bandwidth channel — a
noisy channel's top candidate needs a confidence check + a verify.

## Q: the whole attack's feasibility — what bounds it?

the secret's TTL × the request rate × the channel's bandwidth × the
visit count = the feasibility bound — a low-bandwidth channel × a
rate cap × a short TTL is an infeasible leak — measure all three.
