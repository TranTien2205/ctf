# is it stripped from a HEIC image

**File:** HEIC image — EXIF + item metadata.

**Question:** is it stripped — metadata wiped on upload.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
