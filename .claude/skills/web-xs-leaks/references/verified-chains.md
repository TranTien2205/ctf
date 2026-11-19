# Verified chains — the XS-leak shapes proven in this repository

The verified chain cards and what each actually proves.

---

## The HTB Stylish shape — the CSS unicode-range token-leak

```text
the chain: a sorted 32-char token; a CSP with `font-src 'self' *`
(a host wildcard); a reflected secret in a rendered element; a bot
that visits a target page with a custom-CSS surface.
```

```text
the steps:
1. read the token generator — a sorted character set is recoverable
   via a unicode-range leak
2. read the CSP — `font-src 'self' *` — a host wildcard on fonts —
   the external font host is the exfil channel
3. submit a stylesheet with one @font-face per alphabet char, each
   a distinct URL + a unicode-range
4. the requested font URLs ARE the character-set — sort the leaked
   set → the token
5. a second stylesheet's @font-face src is the SAME-ORIGIN
   privileged URL — the bot's font load is the privileged GET that
   no external client could fire — the channel that read the token
   becomes the channel that spends it
6. a SQLite `LIMIT (SELECT CASE WHEN ... THEN 1 ELSE 0 END)` row-
   count oracle — a blind extraction through the same-origin request
```

```text
the first confirming probe: an external font request from attacker-
controlled CSS — one callback — the falsifier: no callback after
checking the listener/tunnel and the asynchronous stylesheet
publication.
```

## The chain's proven mechanics — what it actually demonstrates

```text
- a @font-face unicode-range oracle is a real char-set channel —
  the font requests ARE the set
- a sorted secret's set IS the answer — the ordering is known
- a font-src wildcard is the exfil — the font host is the listener
- a same-origin stylesheet's @font-face src is a privileged GET —
  the channel that reads is the channel that spends
- a blind row-count oracle extracts through a same-origin request
```

## The chain's constraints — what it requires

```text
- a font-src wildcard ('self' *) — the external font host
- a reflected secret in TEXT (the @font-face reads the rendered
  text, not an attribute)
- a sorted secret — the char-set IS the answer
- a custom-CSS surface — the stylesheet is the carrier
- a bot that renders — a real browser, not a JSDOM
```

## The chain's falsifier — when it doesn't apply

```text
- no font-src wildcard → the @font-face exfil is dead → a different
  channel (a bg-image CSS-selector, a server-state channel)
- a secret in an ATTRIBUTE → a CSS-attribute-selector oracle, not
  a unicode-range
- an unsorted secret → an n-gram beam search, not a direct sort
- a JSDOM bot → no render → no font matching → the channel is dead
```

## The chain's class — what it is and isn't

```text
it IS an XS-leak — the response is opaque; the font requests leak
the secret's shape (the char-set), never the bytes.

it is NOT a CORS read — the response is never read; a JSONP serve —
the endpoint doesn't serve data as JS; a postMessage broadcast —
the page doesn't broadcast.
```

## The proven-beyond-doubt ledger — what the card establishes

```text
- a unicode-range @font-face is a working char-set oracle — verified
- a sorted secret's set IS the answer — verified
- a font-src wildcard is a working exfil — verified
- a same-origin @font-face src is a working privileged-GET channel —
  verified
- a blind row-count oracle extracts through a same-origin request —
  verified
```

## The candidate-vs-proven distinction — what the card does NOT prove

```text
the card proves the MECHANISM works — it does not prove YOUR
challenge has the same surface. your challenge needs:
- a font-src wildcard OR a different exfil directive
- a reflected secret in text OR an attribute (the oracle differs)
- a sorted secret OR an n-gram reconstruction
- a bot that renders (a real browser, not a JSDOM)
run the card's first_confirming_probe on YOUR target before
reusing anything from it — the card is a HYPOTHESIS shape, not a
finding.
```
