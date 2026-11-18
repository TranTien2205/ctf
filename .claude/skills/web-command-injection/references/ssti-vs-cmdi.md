# SSTI vs Command Injection — the boundary call

## Why the distinction matters

The chain card widened this class: `eval()`/expression-evaluator sinks
route HERE (they ARE command injection — the evaluator reaches exec).
True template-injection routes to `web-ssti`. The boundary is *which*
evaluator runs the input.

## The discrimination probe — which syntax evaluates

Send the marker set and see which form produces a computed result:

| Probe | SSTI if works | cmdi/eval if works |
|---|---|---|
| `{{7*7}}` | Jinja/Twig/Handlebars → ssti | — |
| `${7*7}` | FreeMarker/Pebble/EL → ssti | bash/PS/JS-template/EL-eval → eval |
| `#{7*7}` | Thymeleaf/Ruby-erb-in-str | Ruby-string-interp eval |
| `<%=7*7%>` | ERB/EJS/JSP → ssti | — |
| `*{7*7}` / `[[${7*7}]]` | Thymeleaf → ssti | — |
| `7*7` bare in field | — | bare eval/calculator |
| `{{.}}`/`{{this}}` | ssti contexts | — |
| `';id;'` producing output | — | shell |
| `$(id)` producing uid | — | shell substitution |
| `` `id` `` output | — | shell |

The artifact is what the response contains: `49` (math evaluated) means
an evaluator exists — which *kind* of 49 decides the class:

- `49` inside a template-rendered page → ssti
- `49` as raw computed output of a `calc`/`eval` endpoint → eval → cmdi
- `uid=33...` → shell → cmdi
- the marker REFLECTED literally (`7*7` shown) → neither — no eval

## The template-vs-eval overlap — both reach exec

Jinja `{{ ''.__class__...subclasses__() }}` — template syntax reaches
Python objects → `os.system` — the END is the same (exec), the PATH is
ssti. Don't double-count: pick ONE class — the template-form probes
belong to `web-ssti`; the eval-form probes belong here.

## The chain-card overlap note

`htb-pcalc-php-eval` — the input went to `eval($_GET['x'])` directly —
`?x=system('id')` — a PHP eval, NOT a template engine — routed here
because the sink is a code evaluator. The discriminator: PHP code ran
directly, not through a template's compile step.

## When both exist — pick the stronger primitive

An app may have BOTH `{{}}` ssti AND an `eval`/`exec` sink — evaluate:

- ssti needs engine internals (sandbox escapes per engine)
- eval gives direct code — usually a shorter path to exec
- shell-cmdi gives the cleanest command output

Prefer the simplest → try `eval`/`exec` first, ssti if template-shaped.

## Falsifier boundary

- no evaluator accepts arithmetic AND no shell interprets separators →
  neither class
- only `{{}}`/`${}` style works → ssti class, not this

## Output to record

- which wrapper evaluates + the language/shell identified + class
  decision (ssti vs cmdi vs eval)
