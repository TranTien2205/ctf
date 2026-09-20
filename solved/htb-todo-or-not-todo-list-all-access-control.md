# broken authentication control ("TODO OR NOT TODO") — SOLVED (self-solved)

- Platform: HackTheBox (web). Page meta author: makelaris, makelaris jr.
- Date: 2026-09-18
- Target supplied: `http://154.57.164.67:31270` (black-box)
- Flag: redacted; verified live in the `GET /api/list/all/` JSON array
- Cost: 2 probes, ~2 minutes. The whole chain was disclosed by the entry page.

## Chain

1. `GET /` → 200. `Server: made with <3 by makelarides`, `Vary: Cookie`, and a
   Flask signed session cookie
   `session=<b64>.<timestamp>.<signature>` whose first segment decodes to
   `{"authentication":"user9dBa1ecC"}`. No login exists; a visit provisions a
   throwaway user.
2. The entry page carries both halves of the credential in the clear:
   `<input id='data-secret' type='hidden' value='...'>` and an inline script
   `const update = () => getTasks('user9dBa1ecC')`, preceded by the comment
   **`// don't use getstatus('all') until we get the verify_integrity() patched`**.
3. `/static/js/main.js` gives the API: `POST /api/add/`,
   `GET /api/complete/{id}/?secret=`, `DELETE /api/delete/{id}/?secret=`, and
   `GET /api/list/{endpoint}/?secret=` where `{endpoint}` is the username.
4. `GET /api/list/<own user>/?secret=<own secret>` → `[]`.
5. `GET /api/list/all/?secret=<own secret>` → the task list of **`assignee: admin`**,
   seven rows, one of which is the flag. Same session, same secret, only the
   path segment changed.

## The trap that cost the first probe

The session, the username and the secret are **provisioned together per visit**.
My first attempt reused the username and secret from the page I had read
earlier with a *freshly issued* cookie, and both the own-user and the `all`
request returned `{"error":"Not Allowed"}` — which reads exactly like the access
control working. It was not; the triple simply did not match. Parsing the
cookie, the username and the secret out of one single response fixed it and
`all` returned admin's list immediately.

## Reusable lessons

- **A developer comment naming an unpatched function is the challenge.** The page
  named the vulnerable value (`all`), the broken check (`verify_integrity()`) and
  the reason it is broken, before any probe was sent.
- **When a value is issued per session, capture the whole triple in one response.**
  Mixing a stale identifier with a fresh cookie produces an authorisation error
  that is indistinguishable from a correctly enforced control, and that false
  negative can kill a true hypothesis.
- **A magic path segment is a distinct bug from a guessable id.** The check here
  compares the segment to the session user; `all` is special-cased upstream of
  that comparison, so no id enumeration and no cookie forgery were needed. The
  Flask cookie is signed and was never touched.
- Always send the own-object request first. `[]` for my own list versus seven
  rows for `all` is what makes the second response proof rather than a guess.
