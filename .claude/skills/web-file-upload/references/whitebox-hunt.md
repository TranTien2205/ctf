# White-Box Hunt — finding the upload sink and its checks in source

## The grep sequence — sink first, checks second

```bash
# 1. find every upload-capable handler
grep -rn "move_uploaded_file\|\$_FILES\|request\.FILES\|request\.files\|MultipartFile\|IFormFile\|req\.file\|req\.files\|upload\.single\|busboy\|formidable\|express-fileupload\|cgi\.FieldStorage\|Part\b.*getSubmittedFileName\|UploadedFile\|ActiveStorage\|CarrierWave\|parse_multipart\|files\s*=\s*request" \
  --include='*.php' --include='*.py' --include='*.js' --include='*.ts' --include='*.java' --include='*.cs' --include='*.rb' .

# 2. for each handler — find the store call
grep -rn "move_uploaded_file\|\.save(\|shutil\.copy\|file_put_contents\|Files\.copy\|transferTo\|CopyToAsync\|File\.open.*wb\|IO\.copy_stream\|\.mv(\|createWriteStream\|writeFile" .

# 3. find the validators BEFORE the store
grep -rn "mime\|finfo\|getimagesize\|exif_\|imghdr\|Pillow\|Image\.open\|getExtension\|getMimeType\|content_type\|secure_filename\|basename\|pathinfo\|whitelist\|allowed_\|extension\|fileFilter\|file\.mimetype" .

# 4. find the consumers — what reads the stored file later
grep -rn "getimagesize\|exif_read_data\|ImageMagick\|convert \|identify \|ffmpeg\|gs \|pdftk\|wkhtmltopdf\|unzip\|extractall\|phar://\|include\|require\|file_get_contents\|Image::" .
```

## Reading the sink — what to extract

```
save_path = ???           # the path construction — traversal surface
name = ???                # raw name vs sanitized vs generated
ext check = ???           # on the name? the stored name? MIME? content?
MIME check = ???          # header claim vs sniffed
content check = ???       # prefix? structural? re-encode?
consumer = ???            # who reads the file later
serve path = ???          # which route serves it back
```

## The check-order map — which runs first matters

```php
// e.g.
if (ext_bad) reject;
if (mime_bad) reject;
$path = $dir . '/' . $name;      # traversal lives here
move_uploaded_file($tmp, $path);
if (!validate($path)) unlink($path);   # post-store validation = race!
```

The order dictates the attack: ext check first → ext bypass; content check
on tmp → polyglot; check AFTER store → race.

## Where names get sanitized — the critical grep

| Sanitizer | Effect | Still vulnerable to |
|---|---|---|
| `basename($name)` | strips `../` and `/` | `..` inside name gone; NUL/old bugs remain |
| `secure_filename` | ASCII-only + strips | homoglyphs/unicode stripped — bypass moot |
| `Path(name).name` | last component only | `..\` on Windows Python? `.name` doesn't split `\\` on POSIX — `..\\x` survives on Linux-deployed Py3! |
| `FilenameUtils.getName` | last component | handles both separators |
| `path.basename` (Node) | last component | `\\` on POSIX not split — `..\\x` survives |
| `mime/multipart FileName` | pre-1.20 raw | full name |
| `IFormFile.FileName` | RFC-decoded, path stripped | per spec strips `\` and `/` — verify impl |
| regex `[^a-zA-Z0-9._-]` | charset filter | kills traversal and homoglyphs |
| `realpath` + prefix check | containment | catches both traversal AND symlink |
| custom split-on-`.` | `name.split('.')[0]` | strips ALL ext — kills ext tricks but keeps traversal basename |

## The `Path(name).name` / `path.basename` POSIX-backslash trap

On Linux, `Path("../../x.php").name` → `../../x.php` is split on `/` —
`..` components survive? No — `.name` returns `x.php`? Actually
`Path('../../x.php').name` → `x.php` — safe. BUT `Path('..\\..\\x.php').name`
on POSIX → `..\\..\\x.php` (backslash isn't a separator) — the string
survives and writes a file literally named `..\..\x.php` — harmless on
Linux, dangerous if the file ever reaches Windows. Same for Node
`path.basename` on POSIX.

## Find the rename/move calls — the post-store sinks

```bash
grep -rn "rename\|move\|copy.*path\|shutil\.move\|File\.renameTo\|MoveFile" .
```

A rename endpoint taking `from`/`to` paths is a traversal sink independent
of the upload's own name checks.

## Where the flag lives — the post-exec read

Once exec/include/SSTI is proven: grep the source for the flag path —
`/flag`, `FLAG{`, `flag.txt`, `getenv("FLAG")`, env-var names — exec reads
the real location, not a guess.

## The consumer sink grep — second-order surfaces

```
unzip|extract|ZipFile|ZipInputStream|extractall|TarInputStream|tarfile
getimagesize|Image\.open|imagemagick|convert|identify|ffmpeg|gs|pdftk
yaml\.load|pickle|unserialize|Marshal\.load|fromXML|readObject
csv|pandas|read_excel|PHPWord|POI|python-docx|xlrd|openpyxl
wkhtmltopdf|weasyprint|puppeteer|headless|pdflatex|xelatex|tex
```

## Output to record

- the sink file:line + the path construction verbatim
- the sanitizer present/absent + its residual weakness
- the consumer identified + the field that reflects it
