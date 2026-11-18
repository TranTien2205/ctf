# Chunked & Resumable Uploads — tus, multi-part, and split-validation

## The protocols — what the chunked shape looks like

- **tus** (`Tus-Resumable`, `Upload-Offset`, `Upload-Length`, `PATCH` with
  `application/offset+octet-stream`) — headless resumable uploads
- **S3 multipart-style app APIs** — `init → part1, part2... → complete`
- **custom chunked APIs** — `/upload/chunk`, `chunk=N`, `total=M`,
  `session_id`, `upload_id`
- **GraphQL/managed** — upload tokens, finalize calls

## The split-validation bug — only chunk 0 gets checked

The most common CTF shape: validation runs on the first chunk (magic
bytes check, ext check on `init`) — later chunks are concatenated without
re-checking:

```
init:  name=x.png, first-chunk=real PNG header → passes
chunk 1..N: payload bytes                      → appended unchecked
complete → file lands as x.png with the payload inside
```

Probe: send the init with a whitelisted type + real magic bytes, then
deliver `<?php`/payload in chunk 2+. Read back the assembled file.

## The finalize-time checks — where validation re-runs

- `complete`/`finalize` re-validates the whole file — the magic-byte check
  on the assembled content (still bypassable — the polyglot survives if
  it's the same file the whole time)
- `complete` re-validates ext — the final name is what matters
- `complete` checks total size — the accumulated parts

## The "offset" math — where parts land

- `Upload-Offset`/`chunk_index` controlled → overlapping chunks —
  overwrite delivered chunks, rewrite the boundary, land payload at any
  offset
- negative/huge offsets → seek-position games — sparse files, offset
  wraparound
- out-of-order chunks → assembly order differs per implementation

## The name lives in `init` — injection at init time

```
init: {"filename":"../../x.php", "size":N}
init: {"name":"x.png","type":"image/png"}
```

Traversal, ext tricks, name-injection all live at init — the same family
as the single-shot filename field.

## `PATCH`/`POST` method surface — the verbs are part of the bug

tus uses `POST` (create) → `HEAD` (offset query) → `PATCH` (upload) —
each may have different auth/validation. `PATCH` is often the
under-defended one.

## Assembly races — complete before chunks land

- `complete` called early with a partial file → partial stored as valid
- `complete` called twice → double-store / double-process
- `complete` while a chunk is still writing → race window for the
  assembled state

## The session/id guess — hijack another upload

`upload_id`/`session_id`/`file_id` enumerable → `PATCH`/`PUT` chunks into
someone else's upload → inject bytes into their file → or read their
partial file.

## Probe checklist

```
□ does init check only chunk 0?         → payload in chunk 2+
□ does complete re-check?               → needed? polyglot?
□ is offset honored literally?           → overlap/negative/huge
□ is the session id enumerable?          → write into another upload
□ does PATCH skip auth that POST has?
□ does the assembled file get a real serve path?
```

## Falsifiers

- the assembler re-validates the whole assembled file strictly and the
  path is contained
- no chunk/resumable endpoint exists

## Output to record

- the protocol identified + which stage missed validation
- the offset/name field that carried the attack
