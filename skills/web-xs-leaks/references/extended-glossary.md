# Extended glossary — the XS-leak vocabulary, exhaustively

Every term in the class, defined operationally.

---

## The sub-shape terms

**classic shape** — the bot visits YOUR URL → your JS runs on your
origin → a client-side measure (frames.length, onerror, timing).

**sealed shape** — a fixed URL + a script-blocked CSP → no attacker
JS → a declarative (CSS) or server-state channel.

**the deciding question** — can ANY origin the bot reaches run one
line of your JS? a 'no' forces the sealed shape.

## The channel terms

**oracle** — a measurable side-channel that returns a bit or a
character-set about the opaque response.

**frames.length oracle** — a count: one <iframe> per result — the
count is readable cross-origin.

**onload/onerror oracle** — a hit/miss: a 200 vs a 404 — the load
event is the bit.

**timing oracle** — a slow-vs-fast response — performance.now()
measures it.

**cache-probe oracle** — a cached-vs-uncached timing — 'was it
cached' = 'was it visited'.

**`:visited` oracle** — a history read — a visited URL styles
differently (a render-side-channel).

**window.open oracle** — a navigation check — 'did the redirect
happen'.

**scrollHeight oracle** — a content-size leak — a count in the
page's height.

**history.length oracle** — a navigation count — 'how many
navigations'.

**resource-timing oracle** — a load-duration read — 'was it loaded
+ how long'.

## The declarative-oracle terms

**CSS-attribute-selector oracle** — a reflected secret in an
attribute → a selector match → a URL load — the requested URL IS
the match.

**@font-face unicode-range oracle** — a font-src wildcard — one
face per alphabet char → a character-set — the requested font URLs
ARE the set.

**custom-property carrier** — a matching rule sets a --m_* variable
→ an element consuming them as background layers fetches the
matched URLs.

**multi-layer background** — a background-image with N var() layers
→ the browser fetches exactly the matched URLs.

**stylesheet carrier** — a stored/custom-css surface — a <link
rel=stylesheet> + a <div id=trig> — the rules fire declaratively.

## The server-state-oracle terms

**LRU-eviction channel** — a redis --maxmemory-policy allkeys-lru —
a GET that touches a key refreshes it — flood the store → the
survivors are the bot's GETs — a thousand-bit channel.

**counter channel** — a GET that increments a readable counter —
'the counter is N+1' → the GET ran.

**one-shot-token channel** — a GETDEL/single-use nonce — 'did it
survive' is one bit — burns the check — spend it last.

**rate-limit channel** — a bucket with a remaining count — a
consumed quota = 'the GET ran'.

**'last seen' channel** — a timestamp a GET updates — 'the GET ran
at T' — a recency read.

**session-mutation channel** — a GET that mutates a session — 'the
session's value is X' → the GET ran.

## The exfil terms

**listener** — a GET to your server — the classic exfil.

**write-back** — a POST to the target storing the data — an
airgapped exfil.

**DOM-writeback** — the secret rendered visibly — a screenshotting
bot's read-back.

**DNS exfil** — the data rides the DNS subdomain — an airgapped
case.

**postMessage broadcast** — the data broadcast to '*' — a real read
primitive.

## The browser terms

**SameSite=Lax** — a cross-site fetch doesn't carry the cookie; a
top-level navigation does.

**SameSite=Strict** — even a top-level navigation doesn't carry it
on a first-party-only case.

**SameSite=None + Secure** — a cross-site fetch carries it — a
credentialed read.

**meta-refresh** — a same-site navigation issued BY THE TARGET —
bypasses the Lax gate.

**partitioned :visited** — per top-frame site — a same-site or a
render-side-channel only.

**partitioned cache** — per top-frame site — a same-site or a
same-partition read.

**managed policy** — URLBlocklist/URLAllowlist — a forced sealed
shape.

**incognito context** — a fresh session each visit.

**JSDOM** — no render — no CSS, no fonts, no :visited.

**COOP/COEP** — a cross-origin-isolation gate.

## The CSP terms

**script-src 'none'** — no attacker JS — the sealed shape is forced.

**style-src 'unsafe-inline'** — styles survive — the CSS oracle works.

**font-src 'self' *** — a font wildcard — the @font-face exfil works.

**img-src 'self'** — a bg-image exfil blocked.

**default-src 'unsafe-inline'** — a broad hole — check each directive.

**connect-src 'self'** — same-origin fetches only — a write-back works.

## The reconstruction terms

**character-set** — the SET of chars present — the answer for a
sorted secret.

**sorted secret** — 'take N chars, sort them' → the set IS the
string.

**unsorted secret** — the set doesn't order it — an n-gram beam
search.

**n-gram** — an overlapping substring — the markers a beam search
stitches.

**beam search** — a best-first reconstruction over overlapping
n-grams — a noise-aware ordering.

**the blast radius** — the side-effect a destructive channel (an
LRU flood) has on the shared store — possibly the secret itself.

## The class-boundary terms

**a real read** — a channel that returns the DATA (JSONP, postMessage
'*', a `*` ACAO) — a primitive, not a measure.

**a measure** — a channel that returns a BIT about the data — the
XS-leak's whole mechanism.

**a same-site request** — a request whose origin matches the target
— carries the cookie a cross-site one wouldn't.

**the airgapped bot** — a bot that can't reach your listener — a
server-state/write-back channel is the only exfil.
