# what's appended from a PDF document

**File:** PDF document — /Info dict, XMP metadata stream, embedded files, layers.

**Question:** what's appended — data after the end marker.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
