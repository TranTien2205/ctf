# on what device from a PNG image

**File:** PNG image — tEXt/zTXt/iTXt text chunks, eXIf, trailing data after IEND.

**Question:** on what device — the camera/software string.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
