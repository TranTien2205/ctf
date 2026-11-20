# what's appended from a GIF image

**File:** GIF image — comment extension, per-frame metadata.

**Question:** what's appended — data after the end marker.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
