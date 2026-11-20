# when was it taken from a HEIC image

**File:** HEIC image — EXIF + item metadata.

**Question:** when was it taken — create/modify/digitize times.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
