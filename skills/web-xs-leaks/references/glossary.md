# Glossary — the XS-leak vocabulary

Each term's working definition.

---

## The core terms

**XS-leak** — a cross-site leak: the response is opaque but the
browser's side-effects (frame count, error, timing, cache, CSS
match, server-state) leak a bit or a character-set.

**classic shape** — the bot visits YOUR URL → your JS measures a
side-channel (frames.length, onerror, timing, cache).

**sealed shape** — a fixed URL + script-blocked CSP → no attacker JS
→ a declarative (CSS) or server-state channel.

**oracle** — a measurable side-channel that returns a bit or a
character-set about the response's content.

**control pair** — an always-true and never-true condition that
proves the channel works and 'no leak' isn't a broken channel.

## The channel terms

**frames.length oracle** — a count: one `<iframe>` per result,
readable cross-origin.

**error-event oracle** — a hit/miss: onload (a 200) vs onerror
(a 404/500) on a subresource load.

**timing oracle** — performance.now() on a slow-vs-fast response.

**cache-probe** — a second load of a cached resource is faster — a
'was it cached' read.

**`:visited` oracle** — a link to a visited URL styles differently —
a history read.

**CSS-selector oracle** — an attribute-selector match → a custom
property → a background/font URL load — the requested URL IS the
match.

**`@font-face` unicode-range oracle** — a font-face downloads only
when a char inside its unicode-range renders — the requested font
URLs ARE the rendered character-set.

**LRU-eviction channel** — a store with `--maxmemory-policy
allkeys-lru` — a GET that touches a key refreshes it; flood the
store → the survivors are the bot's GETs — thousands of bits.

**counter channel** — a GET that increments a readable counter —
'the counter is N+1 after the bot's visit' → the GET ran.

**one-shot token channel** — a GETDEL/single-use nonce — 'did it
survive the bot's visit' is one bit and burns the check.

## The CSP terms

**script-src 'none'** — blocks ALL script — forces a sealed shape.

**style-src 'unsafe-inline'** — allows inline styles — the CSS
oracle works even when script is dead.

**font-src 'self' *** — a host wildcard on fonts — the external
font host is the exfil channel.

**img-src 'self'** — blocks a bg-image exfil — use font-src instead.

## The browser terms

**SameSite=Lax/Strict** — gates cross-site requests — a cross-site
fetch doesn't carry the cookie; a same-site navigation does.

**meta-refresh** — a same-site navigation issued by the target —
bypasses the Lax gate a cross-site fetch hits.

**window.open** — did the navigation happen — a redirect check.

**scrollHeight** — a content-size side-channel — a content-length
leak.

## The reconstruction terms

**character-set** — the SET of characters present — the answer for
a sorted secret.

**sorted secret** — 'take N chars, sort them' → the set IS the
string.

**n-gram** — an overlapping substring — the markers a beam search
stitches into the secret.

**beam search** — a best-first reconstruction over overlapping
n-grams — noise-aware scoring.

**the blast radius** — the side-effect a destructive channel (an
LRU flood) has on the shared store — possibly the secret itself.

## The class-boundary terms

**a real read** — a channel that returns the DATA (JSONP, postMessage
'*', a `*` ACAO) — not a measure, a primitive.

**a measure** — a channel that returns a BIT about the data — the
XS-leak's whole mechanism.

**a same-site request** — a request whose origin matches the target
— carries the cookie a cross-site one wouldn't.

**the airgapped bot** — a bot that can't reach your listener — a
server-state/write-back channel is the only exfil.
