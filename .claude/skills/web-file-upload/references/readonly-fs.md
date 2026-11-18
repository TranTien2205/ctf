# Read-Only Filesystem Fallbacks — when the upload dir can't be written

## The shape — the target dir is mounted read-only

`EACCES`/`EROFS`/permission-denied on write — the upload "succeeds"
HTTP-wise (200 OK) but the file never lands, or lands in a fallback
path.

## Detection — is the write actually hitting disk?

- `200` on upload + `404` on fetch = write failed silently
- `200` + `200` on fetch but content is empty/different = read-only
  shadow (write went to a tmpfs overlay that got discarded)
- `EROFS` in an error message = kernel-level readonly mount
- `EACCES` = permission-denied — dir not writable by the app user

## The /tmp /dev/shm /RAM-fs escape — writable but not persistent

When the app dir is read-only but `/tmp`/`/dev/shm`/`var/tmp` is
writable — the file lands there but:

- `/tmp` isn't in the webroot — not serveable
- `include '/tmp/x'` still executes it (LFI needs a readable path)
- `/dev/shm` same — exec via include/exec, not via HTTP fetch

A readonly-webroot + writable-/tmp = the LFI-include path (not the
serve path).

## The overlay-fs window — where read-only actually ISN'T

Docker containers: the image layer is read-only but a writable overlay
upper layer exists — writes go to the overlay, which:
- persists until container restart — the file "lands" but dies on restart
- isn't in the image's path — traversal out of the overlay may land in
  the image (read-only) or a volume

## tmpfs/ramfs — speed-upload side-effect

tmpfs = RAM-backed — upload lands in RAM — the file exists until
unmount/reboot — usable for race/exec within the session —
`race-and-temp-files.md`.

## The "the upload dir is ro but the DB dir is rw" — the redirect

When the static upload dir is read-only but the app writes uploaded
content into a database — the file "uploads" as a DB blob — the serve
path goes through a `download.php?id=` read endpoint — a different
attack surface (`file-overwrite.md` — the file lives in a db row not
the fs).

## mmap/`MAP_PRIVATE` — readonly mmap writes don't hit disk

If the app mmaps the uploaded file and you "write" via the mmap —
the private mapping makes the write copy-on-write — the file on disk
never changes — the "write" is illusion.

## Falsifiers

- every writable path is outside webroot/include-path/serve-path
- the app genuinely cannot persist the file anywhere reachable

## Output to record

- the writable-vs-readonly split the upload hits + which dir actually
  persisted (or didn't)
