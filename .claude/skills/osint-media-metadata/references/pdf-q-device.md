# on what device from a PDF document

**File:** PDF document — /Info dict, XMP metadata stream, embedded files, layers.

**Question:** on what device — the camera/software string.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
