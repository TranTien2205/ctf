# what's embedded from a GIF image

**File:** GIF image — comment extension, per-frame metadata.

**Question:** what's embedded — embedded files/objects.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
