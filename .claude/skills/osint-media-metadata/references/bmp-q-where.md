# where was it taken from a BMP image

**File:** BMP image — minimal metadata; trailing data.

**Question:** where was it taken — GPS + landmarks.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
