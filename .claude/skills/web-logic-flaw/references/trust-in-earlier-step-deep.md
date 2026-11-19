# Trust-in-earlier-step deep — the carried-value internals

`trust-in-earlier-step.md` covers the probe. This module is the
mechanism's internals — where carried values live, why handlers trust
them, and the full carrier taxonomy.

## The shape

```js
// step 1 — the server mints a value
const total = cart.items.reduce((s,i) => s + i.qty*i.price, 0);
res.render('checkout', {total});              // → rendered into the page

// step 3 — the handler trusts the returned copy
app.post('/order', (req,res) => {
  charge(req.body.total);                     // the client's copy
});
```

The value traveled server→client→server. The return leg is attacker-
writable; the handler treats it as the same value it minted.

## Why it happens

- **Statelessness**: carrying `total` avoids a server-side recompute —
  the developer "knows" the value was correct when minted.
- **UI-rendered state**: the form displays `total`; the submit handler
  reads the displayed value — conflating display state with store state.
- **Hidden-field convenience**: `<input type=hidden name=price>` —
  "hidden" means hidden from the USER, not from the request.
- **Callback trust**: payment/webhook endpoints trusting the callback's
  claimed outcome.

## The carrier taxonomy

| Carrier | Where it lives | Forge |
|---|---|---|
| hidden field | `<input type=hidden>` | edit before submit |
| JSON echo | `{"price":50}` in step-1 response | mutate in step-3 body |
| cookie | `Set-Cookie: total=50` | resend modified |
| state token | `token=` minted upstream | reuse across flows; forge if unsigned |
| Referer/Origin | headers from "the previous page" | set directly |
| callback body | webhook `{"status":"paid"}` | forge the whole callback |
| session storage | client-readable session bits | depends on signing |

## The probes per carrier

### hidden field / JSON echo

```
GET  /checkout          → note the minted {"total":50}
POST /order {"total":1} → accept? → GET /order/N → "charged":1
```

Evidence is the minted-vs-accepted diff — `50` minted, `1` charged.

### state token

```
step1 → token=T issued for flow F1
start flow F2 → step3 with token=T from F1
```

Does the terminal accept a token minted for a different flow instance?
Unbound tokens replay across flows.

### callback

```
POST /payment/callback {"orderId":N,"status":"paid"}
     — without the payment ever happening
```

The callback's authenticity check is the mechanism: HMAC'd callbacks
verify; unsigned ones take your word for it.

### Referer/Origin

```
POST /admin/action -H "Referer: $BASE/admin" -H "Origin: $BASE"
```

A gate reading `Referer` to mean "came from the admin page" takes your
claim for it.

## The recompute falsifier

`400 price mismatch` / `409 state inconsistent` — the server recomputes
and compares. The falsifier per VALUE: `total` recomputed says nothing
about `discount`, `tax`, `shipping`, `currency`, `orderId` — each
carried value is its own layer. The alphabet of carried values:

- economic: `total`, `subtotal`, `price`, `discount`, `tax`, `shipping`,
  `grand_total`, `amount`, `currency`;
- state: `step`, `state`, `status`, `paid`, `verified`, `completed`;
- identity: `userId`, `orderId`, `cartId`, `session`;
- tokens: `csrf`, `nonce`, `state` (OAuth), `return_to`.

## The composition with other mechanisms

Trust-in-earlier-step composes constantly: a skipped step that also
carries `paid` client-side is skip+trust; a `total` the client mutates
is trust+boundary (`total=-50`). The chain usually needs both edges —
the trust edge delivers the value, the boundary edge makes it
forbidden.
