# is it stripped from a TIFF image

**File:** TIFF image — IFD tags incl GPS.

**Question:** is it stripped — metadata wiped on upload.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
