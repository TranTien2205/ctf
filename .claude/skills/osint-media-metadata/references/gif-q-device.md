# on what device from a GIF image

**File:** GIF image — comment extension, per-frame metadata.

**Question:** on what device — the camera/software string.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
