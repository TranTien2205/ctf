# CTF walkthroughs — the solved shapes, step by step

The three verified local chains plus public writeup shapes, written as
reusable recipes. Provenance lives on the chain cards; this file is the
operational playbook.

---

## 1. htb-nginxatsu — alias traversal → appkey → session forge → blind sqli

The chain shape (the *chain*, not the individual bug):

1. Nginx `alias` misroute — `/static../` style path confusion reads the
   app's `config.json` → `APP_KEY` leaked.
2. `APP_KEY` signs the session cookie → forge `{"user_id":1}` session.
3. The forged session reaches an endpoint that concatenates a stored
   field into SQL → blind SQLi to the flag.

**The reusable piece**: a leaked signing key turns "session" into
"arbitrary identity" — after the forge, the next step is mapping what
the privileged session unlocks.

## 2. htb-tornadoservice — bot + CSRF + class pollution

1. The app accepts a JSON body to a state-changing endpoint without
   CSRF tokens.
2. A planted form in a page the admin bot visits auto-submits — the
   request carries the admin's session.
3. The endpoint does `Object.assign(req.user, body)` — a
   `__proto__.role` or a field-name pollution flips the user to admin.

**The reusable piece**: "session" is the *carrier* — the CSRF fires the
write, the write carries the privileged field, the field wins admin.
All three layers needed, none alone sufficient.

## 3. htb-ssos — OAuth registration race + cookie swap

1. `/register` accepts an `email` and races the uniqueness check — two
   parallel requests both pass.
2. The registration response `Set-Cookie` binds the session to whichever
   request committed last — but the *body* of the response is rendered
   for whichever request wrote the cookie.
3. Cookie-swap the response: the session cookie from request A, the
   rendered account data from request B — your browser is logged in but
   the rendered identity is the other race winner's.

**The reusable piece**: race-condition + session-binding — run
`race_probe.py` on any endpoint where uniqueness should gate the write.

## 4. darkCON GraphQL → session-leak shape

The GraphQL variant: `mutation{login}` returns the session token in the
response body — no `Set-Cookie`. The bug is that the *response* is
cached by the CDN → anyone replaying the cache key gets the token.

**The reusable piece**: tokens in bodies that get cached — look for
`Cache-Control`/`Set-Cookie`/`Authorization` on shared-cache responses.

## 5. HTB Unified — itsdangerous-style session

The `flask-unsign` shape in a Node handout:

1. `session` cookie is `base64(json).timestamp.sig` — decodes to
  `{"_user_id":42}`.
2. `SECRET_KEY` in `config.py` (or `git log` of the handout's `.env`).
3. `flask-unsign --sign --cookie '{"_user_id":1}' --secret leaked` →
  replay → admin.

## 6. corCTF "modernblog" — remember-me token

`remember_me = username + ":" + md5(username + ":" + SECRET)` —
`SECRET` in `.env`. Recompute for `admin` → login as admin without a
password.

## 7. The general writeup pattern

Across the writeup corpus, the solved auth chain is almost always:

```
leak key/secret → forge session/JWT → reach admin endpoint → flag
```

or

```
predict/fixate session id → replay → reach admin endpoint → flag
```

The *forge* and the *reach* are separate steps — don't stop after the
forge.

## 8. The unsolved-shape warnings

The shapes that *look* like auth bugs but aren't:

- "A JWT decodes to `role:user`" — that's just the data.
- "I can set `role:admin` in the body" — check whether `/api/me` honors
  it before calling it a finding.
- "The cookie is `session=<b64>`" — decode it; it's usually just a
  lookup key, not the data.
- "The session id is `JSESSIONID=A001`" — sequential yes, but the
  range may be bounded and per-server — sweep it before claiming.
