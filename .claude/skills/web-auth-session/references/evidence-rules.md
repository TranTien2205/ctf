# Evidence rules — what proves auth bypass and what doesn't

The verdict ladder — the difference between "a signal", "a class member",
and "impact". `hooks.py post-probe` only accepts the excerpt as evidence
when it is a substring of the actual response.

---

## 1. The ladder

| Level | What it is | Verdict |
|---|---|---|
| noise | cookie set, HTML page, token present | never record |
| **surface** | login 200, `Set-Cookie`, decoded JWT claims | `inconclusive` |
| **class** | `alg=none` accepted, `state` missing, predictable sid shape | `confirms` (class) |
| **impact** | forged token accepted on `/admin`, victim session replayed | `confirms` (impact) |

The **class** verdict needs the *mechanism* proved: the verifier accepted
`alg=none`, the session id didn't rotate, the `redirect_uri` allowlist
accepted your host. The **impact** verdict needs the *boundary crossed*:
you reached something you had no right to.

## 2. What does NOT count

- "The login returned 200 with a token." — surface.
- "The JWT decoded to `{"user":"a"}`." — decode is free; the payload
  always decodes.
- "The server accepted `alg:none` in the response." — you still need the
  forged token *accepted on a protected endpoint*.
- "The register accepted `role=admin` in the body without error." —
  accepted-for-storage ≠ used-for-authz; confirm via `/api/me` or an
  admin endpoint.
- "The session cookie has no `Secure` flag." — surface, feeds CSRF/XSS
  class, not this one alone.
- "The `?sid=` param was reflected back." — echo ≠ binding.
- "The reset token looked short." — shape ≠ exploitable until you show
  the range is enumerable.

## 3. What DOES count (by mechanism)

**JWT**: forged token (alg=none / RS→HS / weak secret / kid / jku)
returns `200` and admin data on an endpoint that rejects the original.
The proving excerpt: the response body with the privileged field or the
flag — never just `200`.

**Session fixation**: a session id you chose pre-login returns the
victim's profile post-login. Proving excerpt: the `/api/me` body showing
the victim identity.

**Reset token**: a token minted for account A resets account B's
password, or a token bound to nothing at all. Proving excerpt: the
`200`/`{"ok":true}` on the *victim's* account + the post-reset login.

**OAuth**: `redirect_uri=https://attacker.tld` receives `code=` or
`access_token=` in the Location/fragment. Proving excerpt: the `302
Location:` header verbatim, or your server's access log line.

**MFA skip**: pre-MFA session reaches post-MFA-only data. Proving
excerpt: the admin endpoint body after *only* the first-factor login.

**Session hijack**: a guessed/predicted sid returns a real session.
Proving excerpt: `/api/me` for an account you didn't log in to.

**Mass-assign role**: register/update accepts `role:admin` AND
`/api/me`/`/admin` honors it. Proving excerpt: the `/admin` body.

## 4. `post-probe` shape

```bash
python3 tools/hooks.py post-probe <name> \
  --hypothesis-id H1 --class web-auth-session \
  --verdict confirms --evidence-kind impact \
  --evidence '"role": "admin"' \
  --response '<the verbatim response body>'
```

`--evidence` must appear inside `--response`. `--on-match confirms` on
`http_probe` is for **class**-level; for **impact** the probe must have
actually crossed the boundary — the regex should match the privileged
data, not the status line.

## 5. Negative results worth recording

- alg=none rejected AND RS→HS rejected AND no weak secret found → JWT
  class closed; record `refutes`.
- `state` validated AND `redirect_uri` strict-match AND id_token sig-
  verified → OAuth class closed.
- Session rotated on login AND bound to user AND invalidated on logout →
  fixation/hijack closed.
- `role` field stripped by serializer AND `/api/me` returns `role:user` →
  mass-assign closed for this surface.

Each is a real negative — it tells `decide.py` to change the mechanism
layer, not the payload variant.
