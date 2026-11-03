---
name: web-ssti
description: Prove server-side template or expression injection with nonce-derived arithmetic, identify the engine, and escalate honestly. Use when a value is rendered into a page, an email, a filename or a PDF, or when {{...}} ${...} <%=...%> appears to be evaluated.
classes: ssti
---

# Template and expression injection

Proof requirement: **a nonce-derived arithmetic result rendered by the engine,
with the literal expression absent.**

## Why `{{7*7}}` is not a proof

`49` appears on pages by accident. A product of two four-digit numbers chosen per
probe does not: `proof.template_eval` picks them, substitutes them into your
delimiter, and grades two things — the result is present **and** the expression
is not echoed verbatim. A page that reflects `{{7*7}}` back untouched has proven
only that it reflects.

## The delimiter sweep

One probe per family; stop at the first that evaluates.

| delimiter | engines |
|---|---|
| `{{ a*b }}` | Jinja2, Twig, Nunjucks, Handlebars-ish, Liquid |
| `${ a*b }` | Freemarker, JSP EL, Thymeleaf (`${...}`), JS template literal |
| `<%= a*b %>` | ERB, EJS, ASP |
| `#{ a*b }` | Thymeleaf preprocessing, Pug |
| `{a*b}`, `%{a*b}` | .NET-ish, Struts OGNL |
| `[[${a*b}]]` | Thymeleaf inline |

```
proof.template_eval url="http://t/calc?expr={payload}" expression_template="{{ {a}*{b} }}"
```

`expression_template` is where the delimiter goes; `{a}` and `{b}` are
substituted with the nonce-derived numbers.

## Identify the engine before attempting an escape

This is the step people skip, and it costs more than it saves. The escape from a
template context to code is engine-specific and the wrong payload is
indistinguishable from "not vulnerable". Three cheap identifications:

- **An error.** Deliberately malformed syntax inside the delimiter usually names
  the engine in the stack trace.
- **Introspection.** `{{ self }}`, `{{ config }}`, `{{ 7.__class__ }}`,
  `${ class }` each print something recognisable in exactly one family.
- **The stack.** `recon.fingerprint` already told you the framework, and a
  framework almost always implies its default engine.

## Escalation, and where the proof requirement moves

An evaluated expression is a finding on its own (class `ssti`). Code execution
*from* it is a different class with a different requirement: open an `rce`
hypothesis and prove it with `proof.exec_marker`, nonce and all. Do not report
"SSTI leading to RCE" with only the arithmetic — the ledger records that as a
candidate, and it is right to.

Sandboxed engines are common, and a sandbox that holds is a real result worth
writing down: the expression evaluates, the escape does not, and the finding is
`ssti` with the sandbox named.

## Where the sink hides

Template injection is often not in the page you are looking at:

- a name or subject rendered into an **email** template
- a filename rendered into a **PDF** or a report
- a value rendered into an **error** page rather than the success page
- a field rendered in an **admin** view you cannot see — which makes it blind,
  and the honest route is a collector callback rather than arithmetic
