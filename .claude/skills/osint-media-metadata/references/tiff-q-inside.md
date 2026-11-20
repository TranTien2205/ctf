# what's embedded from a TIFF image

**File:** TIFF image — IFD tags incl GPS.

**Question:** what's embedded — embedded files/objects.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
