# Delivery troubleshoot — when the page doesn't reach the bot

Each delivery failure, its cause, and the fix.

---

## 1. The bot doesn't visit — a /report that doesn't submit

```text
cause: the /report endpoint doesn't take a URL, or a CSRF token
gates it, or the URL format is wrong.
fix: check the endpoint's real signature — a JSON body, a form
field, a query param — grep the source for the submit surface.
```

## 2. The bot visits but JS doesn't run — a CSP block

```text
cause: 'script-src none' or a nonce — the sealed shape is forced.
fix: a declarative channel (CSS → font load) or a server-state
channel — not a client-side measure.
```

## 3. The bot can't reach your listener — an airgapped exfil

```text
cause: the bot can't fetch attacker.com — the classic exfil fails.
fix: a server-state channel (a counter/recency/token you read on
the target), a write-back, or a DOM-writeback — not an external
exfil.
```

## 4. The bot's session isn't the flag-holder's — wrong context

```text
cause: a plain-visitor bot reads a plain session — the flag isn't
in it.
fix: verify the bot's cookie — a flag cookie, an admin context —
grep for 'setCookie|cookie.*flag'.
```

## 5. The managed-policy bot — a forced sealed shape

```text
cause: URLBlocklist ['*'] + URLAllowlist — the bot can ONLY visit
the target's origin — NO attacker URL reaches it.
fix: a declarative/server-state channel — the only channel that
works under a forced sealed shape.
```

## 6. The data: URL — a null-origin case

```text
cause: a data: URL — an opaque/null origin — your JS's origin is
'null'.
fix: a same-origin leak or a server-state read — the null origin's
CORS Origin is the literal 'null'.
```

## 7. The stored page — a same-origin case

```text
cause: a stored page on the target's origin — the stored content's
JS runs on the TARGET's origin — a same-origin channel.
fix: the Lax cookie rides on a same-site navigation — a same-origin
CSS/JS channel.
```

## 8. The JSDOM bot — no render

```text
cause: a JSDOM bot has no rendering engine — no CSS, no fonts, no
:visited.
fix: a DOM/timing/count channel only — frames.length, a count, a
timing — not a CSS/font channel.
```

## 9. The headless bot — a render surface

```text
cause: a headless browser — still renders — the CSS/font/render
channels work.
fix: a real browser renders — the CSS/font channels are live.
```

## 10. The screenshotting bot — a DOM-writeback read

```text
cause: a bot that screenshots the page — no listener needed.
fix: a DOM-writeback — the secret rendered visibly — the screenshot
IS the exfil.
```

## 11. The multiple-visits case — a rate-capped delivery

```text
cause: a low-bandwidth channel needs N visits — a rate cap limits
the /report submissions.
fix: a high-bandwidth channel (a recency, a char-set) — a single
visit — or a smaller marker set.
```

## 12. The single-visit case — a high-bandwidth channel

```text
cause: a recency/LRU channel carries thousands of bits — a single
/report suffices.
fix: a high-bandwidth channel — no sequential visits needed.
```

## 13. The incognito bot — a fresh-session case

```text
cause: an incognito-context bot — a fresh session each visit — the
flag cookie is set per-visit.
fix: the leak reads under the flag-holder's session — verify the
cookie is set.
```

## 14. The fragment — a same-origin navigation

```text
cause: a URL fragment the bot's page reads — a same-origin
navigation to a state.
fix: the fragment carries the delivery — a same-origin read.
```

## 15. The meta-refresh — a same-site navigation

```text
cause: a meta-refresh issued BY THE TARGET — a same-site navigation
— the Lax cookie rides.
fix: the sealed shape's whole design exploits this — the bot's
privileged request is a same-site navigation.
```
