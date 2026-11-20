# what it showed before from a JPEG image

**File:** JPEG image — EXIF in APP1, XMP in APP1, thumbnail in EXIF, comment in COM.

**Question:** what it showed before — the embedded thumbnail.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
