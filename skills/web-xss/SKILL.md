---
name: web-xss
description: >
  Cross-site scripting. Use when a request value reaches an HTML, attribute,
  JavaScript or DOM context and some viewer — usually an admin bot — will render
  it. Identify the context first, then pull references/ per context.
tags: [web, xss, reflected, stored, dom, scripting]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "context unchanged after 2 payload variants"
    - "no reflection or sink point identified"
evidence_level: verified
---

# XSS — Depth Skill

**Verified here.** Chains that prove this class: `htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce`, `htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce`.


## Step 0 — what the flag actually is

In a CTF there is usually a bot that visits a submitted URL. The goal is not a
dialog box; it is to move something the bot can see to somewhere you can read.
Decide first: is the flag in the bot's cookie, in the DOM of a page only the bot
can load, or behind an action only the bot is authorised to take?

If nothing renders the injected markup, there is no flag path here. Return to
`../web-triage/`.

## Identify the context — the step that decides the payload

Send one unique harmless marker and find where it lands.

| Context | First payload shape | Depth |
|---|---|---|
| HTML body | an element with an event handler that fires on load or error | `references/html-context.md` |
| HTML attribute | break out of the quote, then add an event handler | `references/attribute-context.md` |
| Inside a script or a JavaScript string | terminate the string or the script element | `references/js-context.md` |
| A URL-bearing attribute | a script-scheme URL | `references/html-context.md` |
| DOM sink | trace a source such as the location or the fragment to a sink such as an HTML assignment or an evaluation call | `references/dom-xss.md` |

A value interpolated into a template literal inside a script evaluates **before**
any DOM sanitiser runs. Treat that as its own context.

## Exfiltration when the bot fires it

Send the value to a listener you control, or — when the instance has no outbound
access — use the application itself as the channel: have the script write the
value into a record you can read back as an ordinary user. Details in
`references/exfil-methods.md`.

## Filter and policy bypass

Case variation, HTML entity and unicode encoding, handler forms that avoid
parentheses, alternatives to the usual dialog function. Against a content
security policy, look for the site's own allowed script, a leaked nonce, or a
callback-style endpoint. See `references/filter-bypass.md`.

## Variants

When this file lacks the needed variant, open one named file:
`../ctf-web/client-side.md` or `../ctf-web/client-side-advanced.md`.

## Discipline

- Context first, payload second. Do not spray payload families.
- A server-side sanitiser that escapes ampersands means query strings must be
  built at runtime inside the payload rather than stored.
- Bot sessions are often short-lived: verify a stolen credential immediately.
- Fire one payload route at a time, or a success cannot be attributed.
- Context unchanged after two variants means the wrong reflection point or full
  encoding — change layer. See `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.

