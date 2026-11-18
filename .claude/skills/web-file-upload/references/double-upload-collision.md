# Double-Upload & Name Collision — two files fighting for one path

## The shape — two uploads resolving to the same stored name

- same `filename` uploaded twice → second overwrites, appends, or rejects
- two users upload `avatar.png` → same path → who wins?
- a multipart with two `filename="x"` parts → which lands?

The collision is a primitive: overwrite another user's file, or win a
rename race.

## The "last-write-wins" test — does the second upload overwrite?

1. upload `x.png` with marker `A`
2. upload `x.png` with marker `B`
3. fetch — which marker serves?

`B` serves → overwrite allowed → you can overwrite another user's file
(name-guessable) → `file-overwrite.md` (arbitrary overwrite primitive).

## The "same name, different case" test

- `x.png` vs `X.PNG` vs `x.PNG` — case-insensitive fs (NTFS/Windows,
  some macOS) collide them; ext4 preserves
- `X.PNG` uploaded after `x.png` → on Windows the files collide

## The "two parts, same name" multipart quirk — `multipart-spec.md`

Two parts both `filename="x.php"` — first-part vs last-part vs merged —
different parsers pick differently:

- PHP `$_FILES` keeps the last
- some handlers take the first and ignore the second
- some write both appending — content `<?php` in one part, comment in
  other

The probe: two parts same name, different content — which lands?

## The "overwrite another user's file" — the IDOR-by-collision

If the storage path is `<uid>/<name>` and you can control `<uid>` in a
path field — uploading as `victim-uid/avatar.png` overwrites their file
— `authz-and-scope.md`'s scope escape.

## The "the server renames collisions" — `(1)`/`_1`/`-copy` suffixes

`x.png` exists → stored as `x (1).png` or `x_1.png` or `x-copy.png` —
the collision detection is the file-rename step:

- race the collision detection — two simultaneous same-name uploads —
  `race-and-temp-files.md`
- the rename happens BETWEEN check and write — a TOCTOU on the rename

## The "content-based dedup" collision — `checksum-dedup.md`

Same content → same path → overwrite the "same" file's metadata/owner
fields — dedup on identical content vs dedup on filename.

## Falsifiers

- collision names are always renamed AND the rename is atomic
- no way to land on a path another user's file already occupies

## Output to record

- collision policy (overwrite/rename/reject) + which write wins in a
  race
