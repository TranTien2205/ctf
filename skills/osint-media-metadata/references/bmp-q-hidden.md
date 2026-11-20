# what's appended from a BMP image

**File:** BMP image — minimal metadata; trailing data.

**Question:** what's appended — data after the end marker.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
