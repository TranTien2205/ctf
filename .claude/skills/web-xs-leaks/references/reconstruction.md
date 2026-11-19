# Reconstruction — from bits/n-grams to the secret

The oracle returns a character-set, a set of n-grams, or a boolean
per candidate — the reconstruction turns it into the full secret.

---

## 1. The oracle output shapes

```text
a boolean per candidate   → 'does prefix X occur' — a binary search
a character-set           → 'the secret's chars are {a,b,c,...}' —
                            a sorted-string's set IS the answer
an n-gram set             → 'the secret contains abc, abd, ...' —
                            overlapping n-grams to reassemble
```

## 2. The boolean oracle — binary search per position

```python
# 'does the secret start with X' → extend the known prefix
charset='abcdefghijklmnopqrstuvwxyz0123456789'
known=''
while len(known)<32:
    for c in charset:
        if oracle(known+c):   # the CSS-selector / search-oracle
            known+=c; break
    else: break
```

## 3. The character-set oracle — a sorted string's shortcut

```text
a token built by 'take N random chars, SORT them' is fully
determined by its character SET — a unicode-range/font-load oracle
returns the SET directly. sort the leaked chars → the token.
```

```python
# the leaked char-set, sorted — the token for a sorted-string secret
token=''.join(sorted(leaked_chars))
```

## 4. The n-gram oracle — overlapping substrings

```text
a 'does substring X occur' oracle queried over all 1- and 2-gram
prefixes/suffixes plus every 3-gram returns the secret's n-gram
set — the overlapping n-grams reassemble the full string.
```

## 5. The beam search — reassembling n-grams

```python
def beam_search(ngrams, beam_width=10, target_len=32):
    # seed with the highest-scoring n-grams
    beam=[('',0.0)]
    for _ in range(target_len):
        cand=[]
        for s,sc in beam:
            for ng in ngrams:
                if len(ng)>len(s) and ng[:-1]==s[-len(ng)+1:]:
                    cand.append((s+ng[-1],sc+score(ng)))
        beam=sorted(cand,key=lambda x:-x[1])[:beam_width]
    return beam[0][0]
```

## 6. The scoring — log-likelihood over hard yes/no

```text
score each matched n-gram as a log-likelihood ratio calibrated
from the control pair — the always-true control's signal vs the
never-true's baseline — never a hard yes/no: the eviction channel
is noisy.
```

## 7. The reconstruction cost — count it against the budget

```text
a beam search over big integer masks costs seconds per decode —
vectorise it (numpy bitops) or the decode eats the TTL window.
```

## 8. The sorted-secret shortcut — the cheap chain

```text
a sorted secret is the cheap case — a character-set oracle returns
the answer directly. an UNSORTED secret needs the n-gram/beam
reconstruction — the set alone doesn't order it.
```

## 9. The reconstruction-verification — a candidate check

```text
a reconstructed secret must be VERIFIED — submit it where it's
checked, or confirm the reconstruction's confidence score clears a
threshold. a noisy channel's top candidate isn't always right.
```

## 10. The reconstruction-shape table — oracle → method

```text
a 'does prefix X' boolean      → a binary-search extend
a character-set (sorted)       → sort the set — the direct answer
a character-set (unsorted)     → the n-gram/beam reconstruction
an n-gram set                  → a beam search over overlaps
a one-bit-per-visit oracle     → a sequential binary search
a thousand-bit-per-visit       → a set + a reconstruction
```
