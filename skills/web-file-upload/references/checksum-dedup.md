# Checksum/Dedup Uploads — hash-based storage and its gaps

## The shape — the file is named by its content hash

`sha256(content)` or `md5`/`sha1` becomes the filename/storage key:

- `uploads/ab/cd/<sha256>.<ext>` — content-addressed storage
- the same content always lands at the same path — dedup
- a different ext but same content = collision-resistant name

## The collision game — what a hash collision buys

- md5/sha1 chosen-prefix collisions → two files, same hash → overwrite
  another user's file with same-hash yours (their file's entry now
  serves your content)
- sha256 collision — infeasible; only theoretical
- the exploit isn't the collision math — it's the "same hash = same file"
  assumption the store makes

## The "hash the name not the content" trap

- `sha256(filename)` as the key — a filename that hashes to a target's
  key = overwrite; name control = key control — easy collision
- `sha256(content)` but the key uses only a PREFIX — `sha256[:8]` truncates
  to 32-bit — birthday-brute-forceable (~65k attempts to collide)
- `md5(content)[:16]` similar prefix-truncation

## The ext-after-hash append — `<hash>.<ext>`

The stored file is `<hash>.php` where ext is attacker-controlled —
the hash part is fixed (content-derived) but the ext is free — the
exec-ext bypass is still ext-level, the hash doesn't help except
predictability.

## Dedup DoS / storage quirks — the same-file twice

Uploading the same content twice — dedup may:
- return the existing file's URL — predictable URL for your file
- silently no-op — fine
- crash on hash collision handling — a second-order bug

## The "the hash IS the secret" problem

If `<hash>` is treated as unguessable and the file's URL is
`uploads/<hash>.ext` — knowing the content means knowing the URL — the
"unlisted file" isn't hidden.

## Path control through hash parameters

`?sha256=...&ext=php` — if the endpoint trusts a hash param for the
stored name, the path is directly controlled — hash becomes traversal:
`?sha256=../../etc/passwd`.

## Falsifiers

- the hash uses the full digest AND ext is whitelisted AND the path
  isn't a param
- the store never serves the file — hash-naming is internal only

## Output to record

- the hash input (name vs content), its length, and how the URL is built
  from it
