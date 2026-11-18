# Retrieval — finding where the file landed

## The core problem — upload 200 ≠ fetchable

Half the battle is the fetch URL. The app may rename, hash, move to a
sibling vhost, drop into a bucket, or never serve it at all. Retrieval
discovery is a first-class step.

## Sources for the path — ordered by reliability

1. **The upload response itself** — `{"path":..., "url":..., "id":...}`,
   `Location:` header, 201 body
2. **The app's own listing** — `/uploads/` indexable, `/files` API, the
   user profile/avatar URL in a later GET `/me`, thumbnail URL, RSS/list
   endpoints
3. **Front-end JS** — the served-URL template
   (`${id}.png`, `/media/${hash}`) in the bundle
4. **Sibling pages** — the page that displays the upload reveals the URL
   in `<img src>`/`href`
5. **Directory listing** — `/uploads/` 200 + Apache `Index of` — then
   just read the listing
6. **Error strings** — "file already exists at /var/www/x/y" leaks path

## The guess-list — conventional serve paths

```
/uploads/<name>            /uploads/<year>/<month>/<name>
/upload/<name>             /files/<name>           /media/<name>
/images/<name>             /img/<name>             /static/uploads/<name>
/attachments/<name>        /avatars/<name>         /user_uploads/<name>
/data/uploads/<name>       /public/uploads/<name>  /assets/uploads/<name>
/storage/<name>            /storage/app/public/<name>   (Laravel symlink)
/wp-content/uploads/<name> (WordPress)
/sites/default/files/<name> (Drupal)
/media/<name>              /download/<id>          /file/<id>/raw
/tmp/<name> (rare)         /cdn/<name>             /content/uploads/
```

`ffuf`/`feroxbuster` on `/uploads/FUZZ` with the known filename variants
once ONE name is known — or the whole dir listing.

## Rename patterns — when the server rewrites the name

| Pattern | Guess |
|---|---|
| `<uuid>.<ext>` | unguessable — response or listing must leak it |
| `<md5(content)>.<ext>` | computable — you know the content |
| `<md5(filename)>` | computable |
| `<unix_ts>_<name>` | narrow window — brute force ±60s |
| `<user_id>_<name>` | known |
| `phpXXXXXX.tmp` | 6-char brute (feroxbuster + custom wordlist) |
| `file_1`, `file_2` | sequential — enumerate |
| `<sha256(path)>` | unguessable |

Timestamps: the upload response `Date` header bounds the window — brute a
±2-minute range with ffuf over `<ts>_marker.txt`.

## Where files are NOT served — the false-negative traps

- file lands on a worker host, not the web host — `curl` on the web host
  always 404s regardless
- file lands in object storage (S3/GCS) — the app gives a *presigned URL*
  in the response; direct-path guesses miss; check the response body for
  `amazonaws`/`storage.googleapis`/`X-Amz-`/`x-goog`
- file stored in DB — a `download?id=` endpoint re-serves it
- file quarantined/moved — another path
- file served on a DIFFERENT port/vhost — check the app's other ports,
  `Link:`/`Content-Location` headers, the site's `robots.txt`/`sitemap`

## The "is it served at all" discriminator

If a benign `.txt` marker never comes back under ANY enumerable path, the
upload isn't for serving — it's for *processing*. Pivot to
`second-order-processing.md`: importer, thumbnailer, converter, scanner.
The exploitation target becomes the parser, not the URL.

## Verifying the served bytes — `upload_probe verify`

```bash
python3 tools/web/upload_probe.py verify \
  --url "$BASE/uploads/x.php" --expect-source '<?php'
```

Classifies: `served-raw` (source visible — file stored verbatim, run it),
`executed-or-transformed` (bytes changed — code ran or processor touched
it), `blocked`, `gone`. `served-raw` of a PHP file means the dir serves
PHP source verbatim — flag via the source itself or via include chains;
`executed-or-transformed` on a marker payload confirms code execution.

## The "which vhost serves it" trick

Upload `x.txt`, fetch `$BASE/uploads/x.txt`, then fetch the same path on
`static.$HOST`, `cdn.$HOST`, `$HOST:8080`, `media.$HOST` — apps often
split static-serving to a sibling vhost with different rules (no code
exec → then it's an LFI/include problem, not a serve problem).

## Falsifiers

- upload response + app listings + path enumeration find no fetch URL,
  AND no parser ever consumes the file → class closed for THIS surface —
  look for a second upload endpoint

## Output to record

- the exact working fetch URL + how it was learned (response/list/guess)
- the served Content-Type + whether bytes were identical (`cmp`)
- rename pattern if any
