# what's embedded from a PNG image

**File:** PNG image — tEXt/zTXt/iTXt text chunks, eXIf, trailing data after IEND.

**Question:** what's embedded — embedded files/objects.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
