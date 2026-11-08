# CSRF delivery shapes

CSRF is a *delivery* bug: the write endpoint is reachable, the missing piece is
getting a privileged viewer's browser to fire the request. Work the problem in
two halves — what the endpoint accepts, and what a cross-origin page can send.

## The content-type gate

A plain HTML form can only produce `application/x-www-form-urlencoded`,
`multipart/form-data`, or `text/plain`. An endpoint that wants JSON but still
*parses* one of those three is the open door.

**Probe that worked** (TornadoService): fetch a public read endpoint to obtain
a valid object id, then confirm the write endpoint answers `403` for a direct
request — the 403 proves the endpoint exists and rejects *your* auth context;
CSRF is what borrows the viewer's context.

```html
<form method="POST" action="https://target/write">
  <input name="id" value="<fetched-id>">
  <input name='{"k":"v","x":"' value='"}'>
</form>
```

The name/value pair trick (`{"k":"v","x":"` + `"}`) assembles JSON inside a
`text/plain` or urlencoded body when the endpoint's parser is lenient about the
envelope.

## The delivery vectors

| Vector | Sends | Limit |
|---|---|---|
| auto-submit `<form>` | urlencoded / text-plain / multipart POST | content-type only |
| `fetch` with `mode: "no-cors"` | same three content types | cannot read response |
| `fetch` + CORS | any type the preflight allows | needs CORS open — different class |
| `<img>`/`<script>`/`<link>` src | GET only | GET writes only |
| WebSocket | any message | needs ws handshake cross-origin — see `../../web-websocket/` |

## What must not gate it

- `Origin`/`Referer` present but *not enforced* — send with and without to
  measure which the server reads.
- A CSRF token must be *verified against the session*, not merely present — a
  token accepted from another session, or replayed, is no gate.
- `SameSite=Lax` allows top-level GET navigations; a state change reachable by
  GET ships through it. `SameSite=None` + `Secure` allows everything.

## Bot delivery

When the challenge ships an admin bot (`/report`, `/visit`), the form goes on a
page you control and the bot's session does the write. The write's effect —
not the bot's HTTP answer — is the confirmation: poll for the state the write
was meant to create (recorded trap: bots run on a schedule; place the state
first, then poll).

## Falsifier

The endpoint requires a token the attacker page cannot read, or a content type
a form cannot produce — every delivery shape fails and the class closes.
