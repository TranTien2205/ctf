# Evidence Rules — what counts as a read

## The confirm standard — `post-probe --verdict confirms`

- `--evidence` = a VERBATIM substring of `--response`
- `--response` = the actual bytes the request returned
- `--evidence-kind class` for "the read works" vs `impact` for "the
  flag is in it"

## What confirms the class (the read works)

- `root:x:0:0:`/`[fonts]`/`NTFS` — a verbatim file signature
- the file's exact content — `hostname` output, `win.ini`, a config
- `base64` that decodes to a known file — `php://filter` output
- the app's own source — `<?php`/`import`/`package`/`def ` lines

## What does NOT confirm

- a 200 with a generic body — no file content — the read may not have
  run
- an error naming the path — proves the path resolved, not that the
  content echoed
- your own input echoed back — `?file=../../x` → `../../x` — a
  reflection, not a read
- a flag-shaped string that was IN the file-path you sent — not the
  file's content
- a `404` that echoes the cleaned path — a sanitizer oracle, not a read

## The "the file content is the evidence" — the verbatim rule

- `&x;`-style echo of the FILE'S content — not your `?file=` param —
  the echo must be the read result
- the content must be verbatim — `root:x:0:0:` not "I read passwd"

## The "the flag is the content" — the `pre-flag` gate

- the flag appears inside the file's content — verbatim in `--response`
- `python3 tools/hooks.py pre-flag <name> --value "flag{...}" --source
  "<the path you read>"` — the gate decides

## The "the read is a listing" — the dir-list evidence

`file:///etc/` (Java) / `glob://*` — a directory-LISTING is evidence
of a different primitive — record `evidence-kind class` with the
listing — a listing is a read-adjacent primitive, not a file-read.

## The "the hash is the read" — the `md5_file` oracle

`md5_file('/etc/passwd')` returns the hash — evidence = the hash —
matches the known passwd-hash = the file exists — a content-hash
oracle, not a content-read — different evidence-kind.

## The "the metadata is the read" — the existence/size oracle

`file_exists`/`filesize`/`filetype`/`finfo_file`/`getimagesize` — a
metadata oracle — "the file exists" is weaker than "I read it" —
record `surface`-level.

## The "the read is blind" — the timing/error-channel

- timing-delta = fetch-time = the read attempted
- `FileNotFound`/`no such file` = resolves but file missing
- `permission denied` = the file exists but unreadable
- empty response = read worked but content suppressed OR read failed

## The "the read is in a structure" — the field-extract

The content inside `{"data": "..."}`/`The file is: ...` — extract the
field — the verbatim content is the field's value, not the wrapper.

## The "the read is base64" — the decode-and-record

`php://filter` b64 — decode before recording — the `--evidence` is the
decoded content, not the b64.

## The "the negative is a result" — the refutes record

`verdict=refutes` + the verbatim error — `Access denied`/`no such file`/
`EntitiesForbidden`-equivalents — a clean kill is recorded.
