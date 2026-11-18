# Charset tricks — UTF-7, UTF-16, and the encoding-confusion set

The browser decodes the page in some charset — a charset mismatch
between server-intent and browser-decode re-encodes your payload
into different bytes.

---

## 1. UTF-7 — the classic charset XSS

```html
+ADw-script+AD4-alert(1)+ADw-/script+AD4-
   -- UTF-7 encoded <script>alert(1)</script>

+ADw-img src=x onerror=alert(1)+AD4-
   -- UTF-7 img tag
```

UTF-7 uses `+...-` for non-ASCII sequences — `+ADw-` is `<`, `+AD4-`
is `>`. A filter checking `<` `>` in ASCII misses the UTF-7 forms;
if the page is UTF-7-decoded the payload becomes tags.

The gate: the page's charset must BE UTF-7 — which modern browsers
mostly reject as a top-level charset. The surviving variant: a
charset you can inject via `?charset=` or a `Content-Type` you
control, or an old browser.

```html
<meta charset=utf-7>
   -- injected meta forces utf-7 on some browsers — mostly dead
   -- if the response has no charset AND your injection is early
      in <head>, your meta can set it — the HTML5 charset-switch
```

Practical UTF-7: rare today — browsers force utf-8 on most pages.
Listed for completeness; `encodings.md` has the broader set.

---

## 2. UTF-16 — the wide-char variant

```text
< = 0x3C00 (UTF-16BE) or 0x003C (UTF-16LE)
   -- the byte-swapped < — a filter checking 0x3C misses it
```

A page declared UTF-16 decodes your payload differently — only
exploitable if you can set the charset or the page is already
UTF-16. Rare.

---

## 3. The charset-declaration injection

```html
<meta charset="x-user-defined">
<meta charset=utf-7>
<meta http-equiv="Content-Type" content="text/html;charset=utf-7">
```

If your injection lands before the browser commits to a charset
(early `<head>`), you can force a different decode — the page
re-decodes your payload bytes as a different charset.

The ordering constraint: charset must be declared in the first
1024 bytes — a late-injection can't force it.

---

## 4. The `Content-Type`-header tricks

```text
Content-Type: text/html;charset=utf-7
Content-Type: text/html;charset=UTF-16
Content-Type: application/json (the reflecting-response trick —
   a json response carrying your payload renders as text)
```

The reflecting-response content-type — a `?q=<img>` reflection on
an endpoint that returns `application/json` renders the JSON as
text — your tag is text, not markup. Conversely `text/html` always
parses.

The `X-Content-Type-Options: nosniff` gate — with it, the declared
type is honored; without it, the browser sniffs and a `.txt`
response containing HTML may parse as HTML.

---

## 5. The `Accept-Charset` / request-side charsets

```text
Accept-Charset: utf-7    — server may echo in your charset
```

The server honoring your requested charset then reflecting
attacker-bytes → the response decodes in your charset — the
request-side version of the same attack. Rarely honored.

---

## 6. The double-decode charset chain

```text
app reads utf-8 → displays utf-8 → you're in utf-8 — normal
app reads utf-8 → a middleware converts to latin-1 → 0xC3 0xA7
   shows as Ã§ — the "mojibake" bug — a charset-mismatch you can
   exploit if the conversion happens between check and render
```

The practical manifestation: `＜` (fullwidth) survives the utf-8
check, a latin-1 conversion mangles it into bytes that decode as
`<`... contrived — real-world cases exist but need a specific
charset-conversion bug.

---

## 7. BOM tricks — the byte-order-mark

```text
EF BB BF    utf-8 BOM
FF FE       utf-16le BOM
FE FF       utf-16be BOM
```

A BOM at the start of a response can shift the charset sniffing —
some parsers skip the BOM then read the rest as a different
charset. Edge-case territory.

---

## 8. The honest summary — how real this layer is

Charset tricks were THE XSS bypass of the 2005-2010 era — modern
browsers are much stricter. The surviving cases:

```text
- the app lets you set the charset (a ?charset= param or a
  config option)
- a server-side charset-conversion bug (utf-8 → latin-1 → utf-8
  round-trip mangling)
- an old browser target (intranet/legacy apps)
- UTF-7 via specific IE-mode pages
```

For CTF — usually not the first path; try when the byte-level
bypasses are dead AND a charset-config surface exists.

---

## 9. The probe

```text
1. does the response have a charset?  (Content-Type header)
2. can you inject before the 1024-byte mark?  (early <head>)
3. does the app round-trip charsets?        (mojibake test)
4. does an old-browser path exist?           (the bot is always
                                              modern — assume no)
```

All four → charset tricks viable; otherwise skip.
