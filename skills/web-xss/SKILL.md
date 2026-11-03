---
name: web-xss
description: Prove cross-site scripting by context rather than by payload list, and finish with a real browser. Use when a value is reflected into a page, when a payload list is about to be pasted, or when a reflected parameter needs to become a demonstrated finding.
classes: xss
---

# Cross-site scripting

Proof requirement: **a headless browser executing the payload and reporting the
probe nonce.** Reflection is not execution, and the matrix will keep a reflected
payload at `supported` forever — correctly.

## Context is the whole problem

`http.probe` with `token=<a nonce>` reports the parse context the value landed
in. The characters that matter depend only on that:

| context | what you need to leave it |
|---|---|
| `html-body` | `<` and `>` |
| `attribute-value` (quoted) | the matching quote |
| `attribute-value` (unquoted) | a space, or `/` |
| `script-string` | the matching quote, or `</script` |
| `script-body` | nothing — you are already in code |
| `html-comment` | `-->` |
| `url-context` | a `javascript:` scheme, or a `//` host |

A payload list is an attempt to brute-force the answer to a question one probe
answers. Send a nonce, read the context, then send the **three characters** that
context needs. If they come back encoded, the context is closed; say so and move
on.

## The browser is the proof

```
proof.browser_exec url="http://t/search?q=<the payload that writes the nonce>" expect_nonce=<nonce>
```

The payload should write the nonce somewhere the browser reports:
`console.log('<nonce>')`, `document.title='<nonce>'`, or an `alert('<nonce>')`
the tool dismisses. Then `executed=true` plus the nonce is the evidence.

Without playwright installed, the tool says so and the honest route is a
browser driven through the playwright MCP server, with the result recorded via
`ledger.add_evidence kind=browser executed=true nonce=<nonce>`. The matrix grades
it identically — what it will not do is accept reflection in place of it.

## DOM-only cases

The value never appears in the server's HTML; it is read from
`location.hash`/`search` by script. Recon for it in the bundle:
`recon.js_mine`, then look for the sink — `innerHTML`, `document.write`,
`eval`, `setTimeout` with a string, `insertAdjacentHTML`, jQuery `$(...)`,
`location` assignment. The proof is the same browser record; the finding names
the source and the sink.

## Stored cases and the cleanup obligation

A stored payload persists for other users. Three rules:

- use a nonce-bearing payload that is **inert** when it runs: write the nonce,
  nothing else. No cookie exfiltration, no keylogger, no beacon to a third party.
- record where you stored it, in the ledger, as its own evidence record
- remove it when the engagement ends, and record the removal

## Impact, honestly

"Session hijacking" is only an impact if the session cookie is readable from
script — check `HttpOnly` first; `recon.fingerprint` already reported the cookie
flags. With `HttpOnly` set, the impact is what script can do *as the user in the
page*, which is often more interesting and almost always more specific.
