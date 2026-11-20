# what's embedded from a BMP image

**File:** BMP image — minimal metadata; trailing data.

**Question:** what's embedded — embedded files/objects.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
