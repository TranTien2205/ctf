# Corpus index - web-ssti

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

Families present in this corpus, counted from disk. Open the
family's own index or the module whose name matches the
question - do not restate their content here.

| Prefix | Modules | Files |
|---|---|---|
| `README-*` | 1 | `README.md` |
| `advanced-*` | 1 | `advanced-reach.md` |
| `blind-*` | 1 | `blind-ssti.md` |
| `chains-*` | 1 | `chains.md` |
| `cheatsheet-*` | 1 | `cheatsheet.md` |
| `ctf-*` | 1 | `ctf-shapes.md` |
| `detection-*` | 2 | `detection-sequences.md`, `detection.md` |
| `django-*` | 1 | `django-deep.md` |
| `ejs-*` | 1 | `ejs-deep.md` |
| `email-*` | 1 | `email-pdf-artifacts.md` |
| `engine-*` | 2 | `engine-detection.md`, `engine-quirks.md` |
| `error-*` | 1 | `error-pages.md` |
| `extended-*` | 2 | `extended-bypass.md`, `extended-engines.md` |
| `extraction-*` | 1 | `extraction-deep.md` |
| `field-*` | 1 | `field-manual.md` |
| `format-*` | 1 | `format-string.md` |
| `framework-*` | 1 | `framework-contexts.md` |
| `freemarker-*` | 1 | `freemarker.md` |
| `injection-*` | 1 | `injection-points.md` |
| `java-*` | 2 | `java-class-model.md`, `java-other.md` |
| `jinja2-*` | 1 | `jinja2.md` |
| `liquid-*` | 1 | `liquid-handlebars-deep.md` |
| `mako-*` | 1 | `mako.md` |
| `misc-*` | 1 | `misc-engines.md` |
| `neg-*` | 1 | `neg-shapes.md` |
| `node-*` | 1 | `node-engines.md` |
| `nunjucks-*` | 1 | `nunjucks-deep.md` |
| `operator-*` | 1 | `operator-checklist.md` |
| `os-*` | 1 | `os-level.md` |
| `payload-*` | 1 | `payload-dictionary.md` |
| `php-*` | 1 | `php-gadgets.md` |
| `polyglots-*` | 1 | `polyglots.md` |
| `python-*` | 1 | `python-sandbox-deep.md` |
| `ruby-*` | 1 | `ruby-engines.md` |
| `sandbox-*` | 1 | `sandbox-taxonomy.md` |
| `smarty-*` | 1 | `smarty.md` |
| `ssti-*` | 1 | `ssti-bypass.md` |
| `thymeleaf-*` | 1 | `thymeleaf.md` |
| `tooling-*` | 1 | `tooling.md` |
| `twig-*` | 1 | `twig.md` |
| `velocity-*` | 1 | `velocity.md` |
| `work-*` | 2 | `work-boundary2.md`, `work-closing-checklist.md` |
| `workflow-*` | 1 | `workflow.md` |

## Reading order

1. `../SKILL.md` - first probe, falsifier, confirm shape, traps.
2. The `q-*`/`work-*` module matching the question asked.
3. The family module the question lands on.
4. A `*-route` card for the next family when the current one is spent.

## Discipline

Every module here is one piece of the corpus. A claim is a verbatim
response excerpt or artifact record passed through `tools/hooks.py` -
never a line from this index, which is routing information only.
