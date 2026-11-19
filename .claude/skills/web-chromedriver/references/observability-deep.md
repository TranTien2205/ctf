# Observability deep — extracting the maximum signal per iteration

## The instrumentation order

Instrument before the payload runs — hooks attached after the load
miss the early signals:

```python
page.on("console",   lambda m: print("C:", m.type, m.text))
page.on("pageerror", lambda e: print("E:", e))
page.on("request",   lambda r: print(">>", r.method, r.url))
page.on("response",  lambda r: print("<<", r.status, r.url))
page.on("requestfailed", lambda r: print("FAIL", r.url, r.failure))
```

`requestfailed` is the fifth hook most miss — it catches requests that
*left* but failed (CSP block, DNS, TLS), which a `response` hook never
sees because no response arrived.

## The console signal hierarchy

| Console signal | Tells you |
|---|---|
| `console.log` marker | the payload's own breadcrumb — it ran |
| `Uncaught SyntaxError` | the payload's JS is malformed |
| `Uncaught ReferenceError` | a symbol the context lacks |
| `TypeError`/`DOMException` | the payload ran, hit a bad op |
| a CSP `Refused to ...` | CSP blocked a load/connect |
| `Mixed Content` | http:// on an https:// page |

Read the error *type* — a `SyntaxError` is a quoting problem, a
`ReferenceError` is a scope problem, a CSP `Refused` is a policy
problem. Each routes to a different fix.

## The DOM-diff technique

To see exactly where a payload landed, read the DOM around the
injection point before and after:

```python
before = page.locator("#injection-point").inner_html()
# ... payload fires ...
after  = page.locator("#injection-point").inner_html()
```

The diff shows whether the sanitiser stripped, encoded, or rewrote
the value — the rendered truth, not the response body.

## The network-body read

The request log shows a request left; the *body* shows what it carried:

```python
page.on("request", lambda r: print(">>", r.url, r.post_data))
```

A payload's exfil `fetch` carries the flag in `post_data` or the URL —
reading it confirms the *value* left, not just that a request fired.

## The staged-marker technique

For a multi-stage payload, drop a marker at each stage to find where
it dies:

```javascript
console.log('S1: injected');
try { /* stage 1 */ console.log('S2: read ok'); } catch(e){console.log('S2 FAIL',e)}
try { /* stage 2 */ console.log('S3: exfil sent'); } catch(e){console.log('S3 FAIL',e)}
```

The last marker before silence is the stage that died — no guessing
which part of the chain broke.

## The screenshot-diff technique

For a visual payload (a clickjack, a rendered flag), screenshot before
and after and diff the PNGs — a visual confirmation the DOM does not
carry.

## The timing instrumentation

Time the payload's stages against the bot's wait:

```javascript
performance.mark('start');
// ... stage ...
performance.mark('done');
console.log(performance.measure('m','start','done').duration);
```

A payload that takes 4.8 s in a bot that waits 5 s is one iteration
from dead — measure it, do not guess it fits.
