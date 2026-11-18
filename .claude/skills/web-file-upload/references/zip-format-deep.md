# ZIP Format Deep — enough internals to craft slips and polyglots

## The structure — tail-anchored

```
[Local File Header][data][Local File Header][data]...
[Central Directory][End Of Central Directory record]
  EOCD: 50 4B 05 06 | disk | cd-disk | n-entries | total | cd-size |
        cd-offset | comment-len | comment
```

Zip readers find the **EOCD by scanning backwards** from EOF — anything
can precede the first local header: EXE stub, PHP script, GIF image. That
is the polyglot root.

## Local File Header — the entry record

```
50 4B 03 04 | ver | flags | method | mtime | mdate | crc |
csize | usize | name-len | extra-len | name | extra | data
```

Fields that matter for attacks:

- `flags` bit 3 (data-descriptor) — sizes live AFTER the data, not in the
  header — some extractors read the header sizes, some the descriptor —
  a mismatch splits them
- `flags` bit 0 (encrypted) — "encrypted" entries extract garbage or get
  skipped
- `method` 0=store 8=deflate — others (bzip2/lzma) unsupported by some
  extractors → entries skipped or errored
- `name` — the slip surface: raw bytes, `..`, absolute, backslashes,
  encoded
- `extra` — per-tool metadata (UT timestamps, NTFS attrs, unix modes)

## Central Directory — the authoritative index

The CD is what `unzip -l` lists and what most extractors trust for names.
The **local header name** and the **CD name can differ** — a slip is when
the extractor honors one list's name but writes the other's content:

- CD name `ok.txt` + local name `../../x.php` — extractors that use the CD
  name write `ok.txt`; ones that use the local name write `../../x.php` —
  the validator checking the CD-name listing passes the file that lands
  outside
- `zip -FF`/repair tools rebuild the CD from local headers — the two names
  become visible when the tool shows both

Craft: write the zip by hand or patch a `zipfile`-made archive — change
local header name field while keeping CD name.

## The traversal-entry forms — what to emit

```
../../x.php          # POSIX
..\\..\\x.php        # Windows separators inside the name
/x.php               # absolute
..%2f..%2f           # encoded — decoded by a URL-decoding extractor
x/../x.php           # mid-path normalize
a/b/../../../x.php   # nested-normalize
.\..\x.php           # dot-relative
```

`tools/web/archive_gen.py zipslip` emits `../` chains at `--depth N` and
optionally `--absolute` entries.

## The symlink trick — tar and zip

Zip stores symlink as an entry with unix-mode bits set (extra field
`0xA`/`ux` or external attrs). A zip containing `link -> /target` followed
by `link/file` — extractor that honors the mode creates the symlink, then
writes `link/file` through it. `archive_gen.py tarslip` does the tar
version; for zip, hand-craft or use `zip --symlinks`.

## Zip Slip defense forms — and their bypasses

| Defense | Bypass |
|---|---|
| `entry.name.startsWith("..")` check | `a/../x`, encoded `..%2f`, absolute `/x` |
| `new File(dir,name).getCanonicalPath().startsWith(dir)` | symlink inside archive — `link/../..` escaping the realpath check? no — canonical catches it; the win is the defense ABSENT |
| strips leading `/` and `..` | nested `a/b/../../x`, `x/../` normalize mid-path |
| Windows `..\\` filter only | `/` slips on POSIX extractors, vice versa |
| checks CD names only | local-header name differs (above) |

## The `zipfile.extractall` (Python) detail

Modern `zipfile` sanitizes `..`, leading `/`, and drive letters in
`extract`/`extractall` — Python zip slip is dead by default UNLESS the app
iterates `namelist()`/`infolist()` and writes entries itself. Grep that
pattern: `zf.open(n); open(os.path.join(dir, n.filename))`.

## Polyglot construction — script + zip

PHP reads top-down and stops at `?>`/EOF-text; zip reads tail-anchored:

```
<?php ...payload... ?>      ← script at head (PHP outputs rest as text —
                              actually PHP outputs the zip bytes too; use
                              __HALT_COMPILER to cut)
PK\x03\x04 ... PK\x05\x06   ← zip body
```

`__HALT_COMPILER()` stops PHP parsing — bytes after are ignored by PHP,
still read as zip by unzip. Same trick as phar (phar IS this shape).

## `zip -FF`, `jar`, `7z` — alternative readers

- `unzip` (Info-ZIP) sanitizes `..` on extract? — `unzip -d` historically
  did NOT sanitize; newer versions warn. Test the actual tool in source.
- `jar xf` — Java jar tool — follows `java.util.zip` — no sanitize
- `7z x` — does sanitize `..` by default? 7-Zip writes to canonicalized
  paths; absolute entries honored unless `-snld`/flags
- Windows Explorer extract — sanitizes on modern Windows

## The EOCD comment — a stash field

EOCD `comment` is arbitrary bytes some apps surface in "archive info" —
an exfil/injection field for parsers that display it.

## Self-extracting stubs — `PK` + PE/script prefix

`cmd /c copy /b x.exe+y.zip` — a PE stub + zip is already the canonical
polyglot — useful when a validator demands an executable format.

## Falsifiers

- the extractor is a sanitizing one (Python `extractall`, modern 7z with
  `-snl`) AND the app doesn't do per-entry writes itself
- the archive is never extracted — `archive-attacks.md` falsifier

## Output to record

- the entry form that slipped + which side (CD/local) carried it
- the landed path proven by fetch-back
