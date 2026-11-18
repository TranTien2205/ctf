# Extraction Sinks — where unzip/extract/untar lands and what it trusts

## The extractor inventory — who unpacks the upload

| API/tool | Path-sanitize? | Notes |
|---|---|---|
| Python `zipfile.extractall` | YES (modern) — strips `..`, `/`, drives | per-entry `zf.open`+manual write is NOT sanitized |
| Python `tarfile.extractall` | YES since 3.12 `filter='data'`; older — NO | `extractall(filter=)` in 3.11.4+/3.12 |
| `unzip` (Info-ZIP) | sanitizes `..`? — historically NO; newer warns/skips | `-:`/`j` options differ |
| `7z x`/`7zz` | sanitizes by default (`-snld` toggles links) | absolute entries still land |
| `bsdtar`/`libarchive` | `ARCHIVE_EXTRACT_SECURE_*` flags per build | `--no-same-owner`/`insecure` flags |
| Java `ZipInputStream` + naive `new File(dir,name)` | NO | the classic slip — most Java slips live here |
| `java.util.zip`/`ZipFile.getInputStream`+manual | NO | same |
| Apache Commons Compress `ZipArchiveInputStream` | NO | same |
| Node `adm-zip` `extractAllTo` | sanitizes `..` in recent versions | `entryName` raw in `getEntries` |
| Node `unzipper`/`extract` | sanitize varies by version | `path.join` manual writes unsafe |
| `yauzl`/`decompress`/`extract-zip` | varies | `decompress` had slips |
| PHP `ZipArchive::extractTo` | does NOT sanitize `..` (as of many versions) | real slip surface |
| Ruby `rubyzip` `extract` | older versions vulnerable | |
| .NET `ZipFile.ExtractToDirectory` | sanitizes in modern .NET | manual `Entry.FullName` writes unsafe |
| `Expand-Archive` | sanitizes | |

The universal grep — find the exact call:

```bash
grep -rn "extractall\|extractAllTo\|extractTo\|Expand-Archive\|unzip\|ZipFile\|ZipArchive\|ZipInputStream\|tarfile\|TarInputStream\|decompress\|adm-zip\|unzipper\|yauzl\|Archive::Extract" .
```

## The per-entry-write pattern — the slip that survives every fix

```java
// even when extractall-family calls are safe, this pattern is not:
ZipEntry e;
while ((e = zin.getNextEntry()) != null) {
    File f = new File(outDir, e.getName());   // ← name unsanitized
    Files.copy(zin, f.toPath());
}
```

```python
for n in zf.namelist():
    open(os.path.join(out, n), 'wb').write(zf.read(n))
```

```php
$zip->extractTo($dir);   // ZipArchive — checks vary by version
```

White-box: if the code iterates entry names into a `join`/concat, the slip
is open regardless of the library's own `extractall` safety.

## Entry-name details that matter

- `name` is raw bytes — `..`, `/`, `\`, `..\\`, `%2f`, absolute, drive
  letters (`C:\x`), `..\\` mixed
- `name` in UTF-8 vs CP437 — encoding flag bit 11 — a name that's safe in
  one charset is traversal in another
- duplicate names — two entries with the same name: the LAST write wins,
  but a validator may check the FIRST — check-vs-store split again
- `name` vs PAX/extended headers (tar) — `tarfile` reads the PAX `path`,
  a naive reader reads the header name — disagreement

## Tar-specific — the `filter` story

Python 3.11.4+/3.12 `tarfile.extractall(filter=...)`:

- `filter='data'` — sanitizes (names, links, device members)
- `filter='tar'` — blocks absolute/outside links but allows `..` names?
- NO filter arg = fully unsafe on old versions; on new versions defaults
  to a deprecation warning + full trust
- `filter='fully_trusted'` — no protection (explicit)

Symlink/linkname checks inside `filter` — `link.target` escaping is the
slip.

## The "extract to memory then write" — the safe-looking pattern

```python
data = zf.read(name)
safe = os.path.basename(name)          # sanitize check
open(os.path.join(out, safe), 'wb').write(data)
```

Looks safe — `basename` strips `..`/`/` — but on POSIX `basename` doesn't
split `\\` — `..\\x.php` survives on Linux! Also NUL in name — `basename`
keeps it, `open` rejects — a crash is still a signal.

## The second file — resource forks and sidecars

`__MACOSX/` resource-fork entries — extractors write them as siblings;
`.DS_Store`/`desktop.ini`/`Thumbs.db` — mostly noise but some apps read
them. `_rels`/`rels` inside docx get processed as parts not as files.

## After-extract — what the app does next

- walks the tree for a manifest (`plugin.json`, `theme.json`, `setup.py`)
  → the manifest drives the next parser
- serves the extracted dir directly → zip-slip lands directly served
- `require`/`import`/`load` an inner file → RCE by include
- scans each extracted file (second validation — usually weaker than the
  outer)

## The "extraction quota" — bomb defense

Real extractors cap total size/count/ratio; a missing cap is the zip-bomb
sink — `archive-attacks.md`.

## Falsifiers

- the extractor is sanitized AND no manual per-entry write exists AND
  links/devices rejected
- extraction happens in a sandboxed/throwaway context (ephemeral dir,
  dropped permissions)

## Output to record

- the extractor identified + the exact entry form that slipped
- the landed file path + fetch/read-back proof
