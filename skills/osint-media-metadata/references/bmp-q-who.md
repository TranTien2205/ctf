# who made it from a BMP image

**File:** BMP image — minimal metadata; trailing data.

**Question:** who made it — author/creator fields.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
