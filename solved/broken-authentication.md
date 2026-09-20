# broken authentication — SOLVED (self-solved)

- Platform: HackTheBox (web, flag format HTB{...})
- Date: 2026-09-18
- Target supplied: `http://154.57.164.82:31468` (black-box, no source)
- Flag: redacted; verified live in `GET /` body as `<h1>HTB{...}</h1>`
- Time to flag: ~2 minutes, 1 confirming probe, 1 exploit request

## Chain

1. `GET /` → `302` to `/login`; `Server: nginx`, `X-Powered-By: PHP/7.4.12`.
   Page `<title>` is literally `broken authentication`.
2. `/login` HTML gives `POST /auth/login` (username, password) and a link to
   `/register`; `/register` HTML gives `POST /auth/register` (same two fields).
   No front-end JS beyond the vendored template bundle — no other endpoint.
3. Register an account of my own: `POST /auth/register`
   `username=ctfprobe_a1&password=Probe_pw_1` → `302` to `/login`.
4. Log in with it: `POST /auth/login` → `302` to `/`, and
   `Set-Cookie: PHPSESSID=eyJ1c2VybmFtZSI6ImN0ZnByb2JlX2ExIn0%3D`.
   That is URL-encoded base64 of `{"username":"ctfprobe_a1"}` — the whole
   session is client-side JSON, **no signature, no MAC, no server-side store**.
   The cookie is merely *named* `PHPSESSID`; it is not a PHP session id.
5. `GET /` with that cookie renders `<h1>You are not an admin</h1>`, which names
   the exact claim the authorisation check reads.
6. Forge it: `base64('{"username":"admin"}')` = `eyJ1c2VybmFtZSI6ImFkbWluIn0=`,
   sent as `Cookie: PHPSESSID=...` → `GET /` renders the flag in the `<h1>`.

## Reusable lessons

- **Decode the cookie before touching anything else.** A cookie named
  `PHPSESSID` that is not 26 hex/alnum chars but ends in `%3D` (`=` padding) is
  base64, not a session id. One `base64 -d` decided the entire challenge.
- The unauthenticated-but-logged-in page text (`You are not an admin`) leaks the
  field name the check reads, so no guessing of the privileged value was needed.
- Registering my own account was the only write; nothing else was mutated, so
  no cleanup beyond one throwaway user row.
