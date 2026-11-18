# Evidence Rules — what confirms an upload bug and what doesn't

## The ladder — each rung is a different claim

```
upload accepted          → surface — the endpoint exists, nothing more
file retrievable         → surface — storage confirmed; still no exploit
file served verbatim     → class evidence for "no re-encode"; not impact
code executes            → impact — RCE on the box (verbatim output)
file lands over a target → impact — overwrite/template/config proof
consumer runs payload    → impact — XXE hit, parser output, OOB callback
```

## What each verdict needs

### `confirms` (class)

- `upload_probe.py verify` reports `executed-or-transformed` on a payload
  whose marker changed predictably (e.g., `7*7` → `49` in output) — the
  executed output is the verbatim evidence
- `served-raw` of a PHP file where the flag lives in the source
- a polyglot that parses as format-A by the validator AND executes as
  format-B — both proven separately
- a stored-XXE/SSRF callback hit with your canary path in `oob_listener
  hits` — verbatim JSONL line

### `inconclusive`

- upload 200 but file never fetched — storage, not execution
- upload 200 with a path in the response but fetch 404s — path unknown
- "file processed" without visible output — consumer exists but output
  surface unknown
- upload accepted a `.php` — nothing yet proves it executes

### falsifiers — the class is closed when

- no upload is retrievable through any path AND no consumer touches it
- every bypass variant is rejected AND the file is served `attachment`/
  `octet-stream` on a separate static host
- the write root is provably contained (`open_basedir`/chroot) and nothing
  loads an overwritable file

## The verbatim-excerpt rule

`hooks.py post-probe --verdict confirms` requires `--evidence` to be a
substring of `--response`. For uploads the proving excerpt is:

- the executed output of a marker (`49` from `7*7`, `uid=33` from `id`)
- the verbatim `Content-Type`/`Content-Disposition` header set
- the `oob_listener` JSONL line carrying the canary path
- the rendered template output containing your injected string

An error like `Parse error: syntax error in /uploads/x.php on line 1` IS
class evidence — the server ran PHP on your file and choked on it.

## What is NOT evidence — the repeat-offender list

- a 200/201 on the upload POST — surface
- the filename appearing in a JSON response — storage metadata
- a "success"/"ok" body — nothing
- the file listed in a directory listing — presence, not execution
- an upload that "looks like it worked" — measure, don't vibe
- a signature-hit claim (`WAF blocked`) — that's a rejection, not a proof

## The transport trap

A 5xx on the upload endpoint or a connection reset is `transport` — it
says nothing about the validation outcome. Retry before classifying.

## Recording recipe

```bash
# upload_probe verify output IS the evidence quote:
python3 tools/web/upload_probe.py verify \
  --url "$BASE/uploads/x.php?c=id" --expect-source 'uid='
# → executed-or-transformed — paste the verdict + excerpt into post-probe
```

For non-upload_probe paths, `http_probe.py` emits the full `post-probe`
command — `--response` carries the bytes the evidence was read from.

## The "executed" standard

For a payload `<?php echo 6*7; ?>`:

- response body contains `42` where the script would print — impact
- response body contains `<?php echo 6*7; ?>` verbatim — served-raw, not
  execution; the flag may still be inside the source
- 403 on fetch — denied by rule, not executed; try another ext/path
- `X-Powered-By` or error text naming the interpreter — supporting signal

## Output to record

- the verdict per probe + the verbatim excerpt
- the fetch URL + served type + the classify result
- the specific impact proven (exec / overwrite / consumer-hit)
