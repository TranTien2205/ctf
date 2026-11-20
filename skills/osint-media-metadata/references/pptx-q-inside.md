# what's embedded from a Office pptx

**File:** Office pptx — docProps + comments inside the zip.

**Question:** what's embedded — embedded files/objects.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
