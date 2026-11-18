# Windows-Specific Upload Quirks — IIS/NTFS behaviors

## The trailing-dot / trailing-space collapse

NTFS silently strips trailing dots and spaces on create:

- `shell.aspx.` → written as `shell.aspx` — bypasses an ext check on
  `.aspx.` while the file still lands `.aspx`
- `x.asp .` / `x.asp ` → same collapse
- blacklists on `.asp` see `x.asp.` (not in list); the write produces
  `x.asp` — the classic filter-vs-FS disagreement

## Reserved names — CON/PRN/AUX/NUL/COM1-9/LPT1-9

- `con.php` fails to create (device name) — upload error is detection
- the device names exist in EVERY dir — `con`, `con.txt`, `con.anything`
  all reserved on some paths
- an upload that stores `con.txt` works on Linux test, breaks on Windows
  — a fingerprint: error on `con`/`aux` filename → NTFS backend
- `\\?\` prefix paths bypass reserved-name checks

## Alternate Data Streams — `file:stream`

`x.jpg:payload.asp` — writes into the `payload.asp` ADS of `x.jpg`:

- the file's "name" is `x.jpg` — passes ext checks
- `::$DATA` stream is the file content — `x.jpg::$DATA` aliases
- IIS doesn't execute ADS content normally — but `x.asp::$DATA` reads it
  as source in some legacy paths
- NTFS-only — a Linux filesystem writes a file literally named
  `x.jpg:payload.asp` — a fingerprint

## 8.3 short names — `PROGRA~1`, `X~1.ASP`

- `dir /x` shows short names; `PROGRA~1` = `Program Files`
- `x~1.asp` may resolve a file `x*.asp` — a traversal/read via shortname
- IIS tilde vuln (`*~1*/a.aspx`) — historical enumeration primitive
- upload side: a filename colliding with an existing 8.3 alias resolves
  to the wrong file

## Path separator flexibility — `/` vs `\`

NTFS accepts both — `..\..\` and `../../` both traverse. Validation
checking only `../` misses `..\`, `%2e%2e%5c`, `..%5c`, and Unicode
separators — `path-traversal.md`.

## Extension-to-handler — IIS mapping is in `web.config`/mimeMap

`.asp`, `.aspx`, `.ashx`, `.asmx`, `.cer`, `.asa`, `.cshtml` — the exec
exts are the ASP.NET handler set; `.config`/`web.config` uploads modify
mappings — `iis-deep.md`.

## Case insensitivity + normalization

- `X.ASP` = `x.asp` — case-variant blacklist bypass (`.ASP` vs `.asp`)
- Unicode normalization maps chars — `unicode-and-normalization.md`

## The "Windows but not NTFS" edge — FAT/exFAT/UNC

- UNC path `\\share\` in a filename field — an upload to a UNC share is
  remote write
- `%2f`/`%5c` in a URL path reaching a `Server.MapPath`/`Path.Combine` —
  the path handling lives in app code

## Falsifiers

- the server is Linux — Windows quirks inapplicable (detect via error
  pages, `Server:` header, case-sensitivity probes)

## Output to record

- which NTFS quirk the filesystem honors (trailing-dot test tells it)
