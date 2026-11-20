# what's appended from a Office docx

**File:** Office docx — docProps/core.xml+app.xml inside the zip, comments, revisions.

**Question:** what's appended — data after the end marker.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
