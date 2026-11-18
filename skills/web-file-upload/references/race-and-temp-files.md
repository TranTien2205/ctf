# Race & Temp Files — the validate-then-delete window

## The vulnerable shape

```
POST /upload → save to tmp/uploads/shell.php
            → validate (fail!)
            → unlink
```

Between save and unlink the file exists at a fetchable path. Same shape:
`save → validate → rename` (guess temp name), `extract → validate →
quarantine`, `virus-scan queue` (file served while scan pending).

## Detection — the upload-response tells

- `201` then file gone 50ms later — check on a fast fetch loop
- response names a `tmp_`/`pending`/`processing` path component
- upload accepted, then an async "rejected" state — file lives in limbo
- error pages mention quarantine/clamav/pending dir names
- `Set-Cookie`/etag/mtime hints: file present but flagged

## The fetch race — mechanics

```bash
# uploader loop:
while :; do curl -s -F 'f=@shell.php' "$BASE/upload"; done &
# fetcher loop (fire slightly behind):
for i in $(seq 1 500); do
  curl -s "$BASE/uploads/shell.php?c=id" && echo "HIT $i"
done
```

Use `tools/web/race_probe.py` for the controlled shape — overlapping
requests with a serial baseline. For uploads the two arms are the POST and
the GET: `--url`/`--method`/`--body` for arm A, `--url-b`/`--method-b` for
arm B, `--count` is the total alternating a,b,a,b — and `--write-ack` is
required since arm A writes. `--no-barrier` if a barrier sync hurts the
window.

Timing notes:

- ms-resolution: the window is small — parallel requests, keep-alive off,
  no redirects
- retry counts: hundreds of iterations are normal; a single-shot miss
  proves nothing
- varied temp names: `tmp_<random>` — brute force the name? usually the
  upload response leaks it; or the name is deterministic (md5 of content,
  timestamp, session-id + name)

## Predictable temp names — the cheaper win

If the temp name is predictable, skip the race and fetch directly:

```
tmp_<unix_ts>_<filename>        # narrow ts window
<md5(content)>                  # you know the content
<session_id>_<name>
phpXXXXXX                       # PHP tmpnam — 6 rand chars, brute-forceable
upload_tmp_*                    # common prefix + counter
```

Fetch during/right after upload — before the rename/delete fires.

## The "delete" may not be the end — lazy cleanup

- file moved to quarantine dir — still web-reachable at another path
- file renamed with `.quarantine`/`.bad` suffix — still present
- cleanup runs on a cron/worker — hours of window
- validation fails async but the file was already served to another
  request (cache warming)

## Double-upload race — two concurrent uploads to one name

Uploads keyed on filename: two POSTs with the same `filename` interleave
check-and-write — the second overwrites the first's checked state, or the
first's delete removes the second's file leaving a dangling reference.
Useful when validation happens post-save.

## Upload + process race — beat the transformer

`upload → thumbnail/convert → replace original` — fetch the ORIGINAL
before conversion replaces it, when the original carries the payload the
converter would strip.

## Server-side race assists

- `Range`/partial fetches hold connections open — keep the file handle
  alive longer than unlink? No — unlink frees the name, not the inode;
  `Accept-Ranges` fetch after delete returns 404
- keep the file via an open fd through `?download` streams — irrelevant
  once the path is gone
- hold the upload POST slow (dribbled body) — validation may run on a
  partial file while the full payload still streams in — check whether
  validation is mid-stream or post-close

## White-box signature

```python
# the pattern to grep:
tmp = save(file)          # store first
if not validate(tmp):     # then check
    os.remove(tmp)        # then delete
```

vs safe order:

```python
if not validate_bytes(file):  # check the bytes FIRST
    reject()
save(file)
```

Grep: `validate.*unlink|is_valid.*remove|scan.*delete|reject.*unlink` and
upload handlers that write before checking.

## Falsifiers

- validation is byte-level on the request body BEFORE any write — no file
  ever exists at a fetchable path
- the temp/quarantine path is outside any served root
- the race window provably closed (verified with overlapping requests —
  `race_probe.py` overlap measurement inconclusive = not a real race)

## Output to record

- the window proven (overlap confirmed, not just an anomaly once)
- the fetch URL that hit inside the window + iteration count
- the exact ordering in source if white-box
