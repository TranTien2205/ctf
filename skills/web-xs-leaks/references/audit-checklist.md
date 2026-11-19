# Audit checklist — a self-audit for an XS-leak

The checklist that catches a wrong analysis before it wastes time.

---

## The sub-shape — did I name it

```text
[ ] CLASSIC — the bot visits MY URL → my JS measures a side-channel
[ ] SEALED  — a fixed URL + script-blocked CSP → a declarative/
              server-state channel
[ ] the deciding question — can ANY origin the bot reaches run my JS?
```

## The channel — did I pick one that exists

```text
[ ] a frames.length surface — a per-result iframe
[ ] an onload/onerror surface — a 200/404 search
[ ] a timing surface — a slow-vs-fast path
[ ] a cache-probe surface — a cached resource
[ ] a :visited surface — a history read
[ ] a CSS-selector surface — a secret in an attribute
[ ] an @font-face surface — a font-src wildcard
[ ] a redis LRU — the eviction channel
[ ] a counter — the read-back channel
[ ] a one-shot token — the single-use flag
[ ] a rate-limit — the quota channel
[ ] a 'last seen' — the recency channel
```

## The control pair — is it built

```text
[ ] an always-true control — a URL/selector that always hits
[ ] a never-true control — a URL/selector that never hits
[ ] a YES hit + a NO miss — the channel works
[ ] a NO hit → 'no leak' is a broken channel, not a negative
```

## The feasibility — did I check the arithmetic

```text
[ ] the secret's TTL — the whole leak+decode+submit fits the window
[ ] the request rate — thousands of markers need tens-hundreds rps
[ ] the bits/visit — a token=1, a recency=thousands, a CSS=a char-set
[ ] the char-set — a sorted/limited alphabet reduces the search
[ ] the bot's context — a flag-holder session, not a plain visitor
```

## The delivery — does the page reach the bot

```text
[ ] a /report endpoint — the URL the bot opens
[ ] a data: URL — an airgapped/null-origin case
[ ] a stored page — a same-origin case
[ ] a managed-policy bot — a declarative channel only
[ ] an airgapped bot — a server-state/write-back
```

## The exfil — does the data reach me

```text
[ ] a listener — the classic exfil
[ ] a write-back — an airgapped case
[ ] a DOM-writeback — a screenshotting bot
[ ] a server-state read — a counter/recency/token
```

## The reconstruction — does the leak assemble

```text
[ ] a sorted secret — a char-set IS the answer
[ ] an unsorted secret — an n-gram beam search
[ ] a boolean oracle — a binary-search extend
[ ] a count oracle — a length-first + a char-by-char
[ ] a noisy channel — a beam + a confidence + a verify
[ ] a one-bit channel — N queries — check feasibility
```

## The spend-order — is the one-shot last

```text
[ ] a GETDEL/single-use token — spend it LAST
[ ] the cheaper channels narrow the answer first
```

## The blast-radius — is the channel destructive

```text
[ ] an LRU flood — does it evict the secret's own key
[ ] a shared store — is the instance yours alone
```

## The verify — is the confirm real

```text
[ ] a reconstructed secret is a CANDIDATE until verified
[ ] submit it → confirm acceptance
[ ] a confidence score clears a threshold
[ ] 'the oracle fired' ≠ 'the secret leaked'
```

## The confusables — is it really an XS-leak

```text
[ ] a fetch READS bytes — web-cors (a real read)
[ ] a WRITE — web-csrf
[ ] a JSONP/postMessage broadcast — a real read primitive
[ ] a stored response — web-cache-poisoning
[ ] a script-tag serve — a real read primitive
[ ] the response is OPAQUE — web-xs-leaks (a measure)
```

## The falsifier — is the surface dead

```text
[ ] a sealed shape with no CSS oracle AND no server-state channel
    → a different class
[ ] an airgapped bot with no server-state read → a write-back or
    a different class
[ ] a secret not in an attribute AND not in text → no CSS channel
```
