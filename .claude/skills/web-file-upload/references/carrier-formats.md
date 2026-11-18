# Carrier-Format Deep — 7z/rar/gzip/bz2/xz/zstd specifics

## The format table — which extractors accept what

| Format | Magic | Traversal notes |
|---|---|---|
| `.zip` | `PK\x03\x04` | `zip-format-deep.md` — the standard |
| `.tar` | `ustar` at 257 | no compression — raw header, `../` in names |
| `.tar.gz`/`.tgz` | `1f 8b` + tar inside | double-layer — outer gzip, inner tar names |
| `.tar.bz2` | `BZh` + tar | same inner names |
| `.tar.xz` | `FD 37 7A 58 5A 00` | xz streams concatenated — extra blocks ignored |
| `.tar.zst` | `28 B5 2F FD` | zstd |
| `.7z` | `37 7A BC AF 27 1C` | symlink+hardlink flags, `../` names |
| `.rar` | `52 61 72 21 1A 07` | NTFS ADS, volume names |
| `.gz` (bare) | `1f 8b` | single-file gzip — extracted filename from FNAME field or stripped `.gz` |
| `.bz2`/`.xz`/`.zst` bare | various | same single-file pattern |

## The nested-compression shape — tar inside gzip inside gzip

`x.tar.gz.gz` — extract outer gzip → `x.tar.gz` → extract again → tar —
each layer's name field is a fresh traversal vector. The multi-layer
nesting is the depth limit test — `zip-bombs-deep.md` for the nested
bomb version.

## `tar` symlink/hardlink entries — `symlink-upload.md`'s carrier

`tar` has real SYMTYPE/LNKTYPE entries — `tarfile.extract` honors them
unless filtered; `zipfile` ignores the zip-link flag. Tar is the more
link-capable carrier.

## `7z` — the featureful one

- `.7z` header can declare `kSfx`/`kVolume`/`kAltStreams`
- `p7zip`/`7z` honors `../` names without check
- the `.7z` format supports "empty" streams that map to nothing — a
  naming-only entry

## `.rar` — the NTFS edge

RAR supports `file:stream` ADS names natively — extracting a rar whose
entry is `x.jpg:evil.asp` writes into an NTFS ADS — `windows-quirks.md`.

## The `FNAME` field in gzip — a naming primitive inside the header

Bare `.gz` carries an optional `FNAME` field — extractors that honor it
name the output file by the header — `FNAME=../../x` inside a gz = the
traversal isn't in a zip/tar name field, it's in the gzip metadata.

`archive_gen` covers zip/tar/phar; gzip FNAME is a manual craft.

## The "the extractor IS the bug" — the decompressor itself

- `unrar`/`7z`/`tar` itself has CVEs — path handling in the TOOL, not
  the format
- `tarfile.extract` without `filter='data'` — the classic python trap
- `ZipFile.extractall` vs `.open()` — the API choice decides

## Falsifiers

- no archive format is processed
- the extractor uses `filter='data'`/strict path-normalization AND
  ignores symlinks

## Output to record

- which carrier the extractor accepts + which path-normalization it does
