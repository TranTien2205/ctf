# Corpus index - web-xss

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

Families present in this corpus, counted from disk. Open the
family's own index or the module whose name matches the
question - do not restate their content here.

| Prefix | Modules | Files |
|---|---|---|
| `README-*` | 1 | `README.md` |
| `attribute-*` | 1 | `attribute-context.md` |
| `blind-*` | 1 | `blind-xss.md` |
| `bot-*` | 1 | `bot-chains.md` |
| `charset-*` | 1 | `charset-tricks.md` |
| `cheatsheet-*` | 1 | `cheatsheet.md` |
| `contexts-*` | 1 | `contexts.md` |
| `csp-*` | 1 | `csp.md` |
| `css-*` | 1 | `css-exfil.md` |
| `dangerous-*` | 1 | `dangerous-apis.md` |
| `detection-*` | 1 | `detection.md` |
| `devtools-*` | 1 | `devtools-workflow.md` |
| `dom-*` | 2 | `dom-clobbering.md`, `dom-xss.md` |
| `encodings-*` | 1 | `encodings.md` |
| `events-*` | 1 | `events.md` |
| `exfil-*` | 1 | `exfil-methods.md` |
| `filter-*` | 1 | `filter-bypass.md` |
| `framework-*` | 1 | `framework-sinks.md` |
| `gadgets-*` | 1 | `gadgets.md` |
| `headers-*` | 1 | `headers-xss.md` |
| `html-*` | 1 | `html-context.md` |
| `js-*` | 1 | `js-context.md` |
| `markdown-*` | 1 | `markdown-render.md` |
| `mutation-*` | 1 | `mutation-xss.md` |
| `neg-*` | 1 | `neg-shapes.md` |
| `operator-*` | 1 | `operator-checklist.md` |
| `payload-*` | 1 | `payload-dictionary.md` |
| `polyglots-*` | 1 | `polyglots.md` |
| `postmessage-*` | 1 | `postmessage.md` |
| `protocols-*` | 1 | `protocols.md` |
| `reflected-*` | 1 | `reflected-xss.md` |
| `second-*` | 1 | `second-order-dom.md` |
| `self-*` | 1 | `self-xss-to-real.md` |
| `source-*` | 1 | `source-sink-table.md` |
| `stored-*` | 1 | `stored-xss.md` |
| `svg-*` | 1 | `svg-deep.md` |
| `unicode-*` | 1 | `unicode-deep.md` |
| `upload-*` | 1 | `upload-xss.md` |
| `waf-*` | 1 | `waf-specific.md` |
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

## Context order

Measure the contexts cheapest-first: body, then attribute, then JS
string, then DOM sink. Each context has its own payload grammar and
its own sanitizer boundary - a payload that died in the body may
land unencoded inside an attribute or a JS string. The context that
reflected unencoded is the one the exploit builds on; the others are
recorded negatives.

## Bot note

A stored or reflected payload only becomes XSS when a viewer renders
it - the challenge's admin bot, a real user flow, or your own
headless reproduction (the chromedriver skill covers driving one
yourself). 'Payload rendered in my own session' is a candidate;
'bot fetched the marker' is the record.

## Budget note

Five probes per context, then pivot contexts - not five variants of
one payload in one context.

## Encoding note

The encoding a sanitizer applies is the boundary, not the obstacle:
HTML-entity encoding kills the body context but not necessarily an
attribute that never needed `<`; JS-string escaping kills the
quote-break but not the template-literal or the newline. Each encoding
is measured, never assumed - the sanitizer_fuzz differential sweep
exists for exactly this.

## Chain note

Once execution is proven in any context, the next question is what the
session gives the script - cookie flags, CSRF-token legibility, the
admin bot's reachable functions. Execution is the class boundary;
impact claims live in the response the payload produces.

## Ledger note

Each context gets its own line in the hypothesis ledger: context,
payload shape sent, verbatim response slice, verdict. Closing the
class is an AND over all reachable contexts - not the first refusal.

## Stop condition

The class closes when every reachable context was measured and
refused, or when a verbatim execution record exists - whichever first.
