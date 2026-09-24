# secure-email-service (picoCTF / corCTF) — web

Flag source: live response (`GET /api/emails`). Flag value not recorded here.

## Shape

FastAPI + uvicorn on Python **3.11.8**. Users hold S/MIME certs issued by a root
CA; `/api/send` builds the mail with Python's `email` package and signs it with
`python-smail`. The front end verifies with an OpenSSL **WASM** build and parses
with a second WASM binary — Rust **`mail-parser` 0.9.4`**. `email.html` renders
the verified HTML into `shadow.innerHTML` with no sanitiser. An admin bot
(playwright) stores the flag in `localStorage` and replies to the newest mail.

## The differential

Two parsers disagree about the same bytes, and a third component generates them:

| Component | Behaviour |
|---|---|
| Python 3.11.8 `email.generator` | guards `Subject` with only `re(r'\n[^ \t]+:')` — `verify_generated_headers` did not land until 3.11.11 |
| Rust `mail-parser` 0.9.4 | accepts `Header : value` **with whitespace before the colon** |

So `Subject: x\nFrom : admin@ses` is written verbatim by Python and read by
mail-parser as a real `From` header that **overrides** the genuine one. The bot
therefore replies to *itself*, putting an admin-signed message in its own inbox.

## Chain

1. `/api/password` → creds for `user@ses`.
2. RFC 2047 encoded-word in `Subject` → `parsed.subject` carries **raw CRLF**.
   `reply.html` feeds it straight back as `` `Re: ${parsed.subject}` ``.
3. That string is used twice by `/api/send`: as the `Subject` header **and** as
   `template.render(title=...)`, so the injected lines land inside the *signed*
   `multipart/mixed` part bodies.
4. jinja2 autoescapes, so the payload is smuggled as **UTF-7** (`+ADw-` = `<`):
   it contains none of `&<>"'`, so escaping is a no-op, and mail-parser decodes
   the injected part (`Content-Type : text/html; charset=utf-7`) back to real tags.
5. The injected part needs the *real* inner boundary. `_make_boundary()` uses
   `random.randrange(sys.maxsize)`, so CPython's MT19937 is recovered from 640
   observed boundaries — each leaks one full 32-bit word plus 31 bits of the next.
6. Two bot runs: the first makes the admin self-reply with the payload, the
   second renders it. The XSS reuses the admin's own `localStorage.token` to
   `POST /api/send` the flag to `user@ses` — entirely in-band, no egress needed.

## What cost the most time

The injected delimiter **is itself part of the message text**, so
`_make_boundary()` saw `^--<b>(--)?$`, treated it as a collision and re-rolled the
boundary to `<b>.0`. The prediction was correct and the exploit still failed
silently. A single **trailing space** on the delimiter line defeats that anchored
regex while remaining a legal RFC 2046 delimiter that mail-parser accepts.
