# Auth & Scope — who may upload where, and how the check fails

## The gate layers — where auth actually lives on uploads

```
endpoint auth middleware   → /admin/import needs admin role
field-level auth           → "path" field only honored for admins
storage-level auth         → write to /admin/uploads only for admin workers
serve-level auth           → /uploads/* public but /internal/* needs auth
```

Each layer can disagree — the endpoint requires login but the upload
handler inside runs on behalf of anyone the endpoint forwards to.

## The "upload is public but processing is admin" trap

The classic CTF shape: anyone uploads; an admin (or the admin's bot)
views/processes it — the attack targets the *processor/bot*, not the
endpoint. The auth question becomes "does the bot/admin read my file" —
`second-order-processing.md` + bot-side payloads (`svg-attacks.md`,
`document-attacks.md`).

## Role-gated upload endpoints — the bypass list

- a role-check on the page but not the POST handler (state-changing verbs
  under-protected) — try the POST directly
- role checked on `GET /upload` but not `POST`/`PUT`
- `X-Forwarded-Role`/`X-User-Role`/`role` cookie param honored
- JWT role claim — `web-auth-session`
- IDOR on the upload path — `POST /users/<id>/avatar` for another id
- `is_admin` flag inside the multipart body honored by the handler

## The "my files vs others' files" boundary — IDOR on stored files

- `GET /files/<id>` serves another user's upload — IDOR read
- `DELETE /files/<id>` deletes another's
- `PATCH/PUT` overwrites another's — overwrite their config/template
- name collisions — uploading `x.php` when `x.php` exists — who wins?
  overwrite of another user's file = a targeted overwrite primitive
  → `file-overwrite.md`

## Signed-upload URL scope — who can sign for what

`getUploadUrl?path=...` — a signing endpoint that signs arbitrary keys —
the presigned URL is the write primitive; key traversal `../../` inside
the path param → `cloud-storage.md`.

## Upload + IDOR the classic shape

- upload to `/users/<victim>/avatar` — overwrite their avatar (deface)
- upload to `/teams/<tid>/...` outside your team — scope escape
- `path`/`dir` fields that embed a user id — traversal across tenants

## The "logged-out upload" — anonymous surface

Public-facing upload endpoints (contact forms, "report a bug" attachments,
anonymous pastebins) are the first probe — anonymous write + retrieval =
anonymous file host, sometimes directly exploitable.

## Auth on the SERVE side — the file exists but you can't read it

- `/uploads/x` requires login — your own session works; an admin's view
  of it is the real test (their bot reads it)
- presigned/serve tokens expire — re-fetch the URL
- `Referer`-gated serving — add `Referer: $BASE/` header on fetch
- `Range`-only serving — partial reads allowed, full 403

## Falsifiers

- the upload endpoint is fully gated AND no path reaches it unauthenticated
- the bot/admin never reads uploads — consumer doesn't exist

## Output to record

- which auth layer failed + the verbatim evidence of the cross-scope write
