# Verified chains — the two cards that proved this class

Two solved challenges in this repository prove `web-race-condition`. Each
carries the probe that already worked, the traps, and the blast radius — read
the card, run its probe, don't re-derive it.

---

## Card 1 — ApexSurvive: profile race → crossed token → template-literal XSS → file-write → template RCE

`knowledge/chains/htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce.json`

### The primitive — the race

```text
the profile update mints a token for the new email, commits the change, then
re-reads the address and calls sendEmail — mint and send are not atomic.

A: POST /profile {email: a@x}   → mint Ta, commit email=a@x
B: POST /profile {email: b@y}   → lands before A re-reads, commit email=b@y
A: re-reads → gets b@y          → sendEmail(b@y, Ta)
result: token Ta, minted for a@x, is delivered to mailbox b@y — which you read.
```

- **Confirming probe**: send two interleaved profile updates; observe which
  address receives which token. Expected: a token belonging to one address
  arrives at the other.
- **Falsifier**: the token is read inside the same transaction as the update —
  then each token reaches only its own address.

### The chain after the race

| Step | Stage | What the primitive bought |
|---|---|---|
| 1 | primitive | race delivers another address's token to your mailbox |
| 2 | pivot | store a note rendered inside a template literal — one interpolation + closing backtick runs before the DOM sanitiser (DOMPurify/bleach) sees it |
| 3 | exfil | the admin bot's own script creates an item carrying its cookie — the app is the exfil channel when outbound is blocked |
| 4 | sink | the admin file-write takes a path-joined filename inside a *valid* PDF — payload bytes ride the content stream past the parser check |
| 5 | flag | overwrite the template a route renders with a Jinja expression; hit a worker that never cached it — RCE without a reload |

### The traps the card records

- **Do NOT overwrite the server config or an imported module to force a
  reload** — that is the step that bricks instances. The template cache is
  per-worker; with several workers, one that never rendered the route still
  loads the file fresh — the flag arrives without any reload.
- The sanitiser operates on the DOM *after* the template literal was
  evaluated — a single `${...}` + a closing backtick is enough.

### Blast radius

`overwriting server configuration or an imported module can permanently break
the instance` — stay on the template-file overwrite, never the config/module.

## Card 2 — SSOS: registration race → cookie-swap JSON CSRF → flag-in-your-account

`knowledge/chains/htb-ssos-oauth-registration-race-cookie-swap-json-csrf.json`

### The primitive — the race

```text
the bot's startup does registerUser(fixed account: student@domain).
win the race by hammering POST /api/register for that account with your
password before the bot reaches its register step.

you now own the account the bot thinks it owns — its later login fails (your
password ≠ its stored one), so its shared SSO token cookie stays bound to your
account.
```

- **Confirming probe**: hammer `POST /api/register` for the fixed bot account
  with your own password and confirm it returns `200` before the bot reaches
  `registerUser`. Expected: registration succeeds and your credentials work at
  `/api/login`.
- **Falsifier**: the account is already registered with an unknown random
  password → the instance is already consumed.

### The chain after the race

| Step | Stage | What the primitive bought |
|---|---|---|
| 1 | primitive | win the registration race → own the bot's account |
| 2 | pivot | spray `/submit-url` with a `data:text/html` URL whose `text/plain` form does a cross-site JSON login to the SSO API for your account — Gin's `ShouldBindJSON` parses the raw body as JSON regardless of Content-Type, and the `Set-Cookie` swaps the shared token (no SameSite) |
| 3 | exfil | the bot's `loginSSO` ignores its credentials and authorizes on the *current* shared token cookie → the flow binds your account |
| 4 | sink | the bot submits the flag at startup into the account it thinks is its own — which is yours; read `GET /submission/:id` as the author |

### The JSON-CSRF mechanics the card records

- `ShouldBindJSON` (Gin) parses the body as JSON no matter the `Content-Type`.
- A `text/plain` form whose input *name* is the JSON prefix and *value* is the
  closing brace submits a valid JSON login cross-site.
- The login response `Set-Cookie` overwrites the shared SSO token — the
  missing `SameSite` is what lets the cross-site POST set it.

### Blast radius

`a fresh instance is required; an already-running instance is permanently
consumed because the flag is submitted once at startup into an account with an
unknown random password` — the race is one-shot and unrecoverable on a used
instance.

## The two patterns these cards establish

| Pattern | ApexSurvive | SSOS |
|---|---|---|
| what's raced | a token's delivery address | an identity's registration |
| crossed state | token to the wrong mailbox | you own the bot's account |
| why it pays | account primitive → stored field → bot | confused deputy → flag lands in your mailbox |
| the sink | template-overwrite RCE | read the flag submission |
| blast radius | template file only, never config/module | fresh instance required, one-shot |

The common lesson: **the race buys the foothold, not the flag.** Both cards
end in a different bug class — XSS, CSRF — because the race is always the
primitive provider.
