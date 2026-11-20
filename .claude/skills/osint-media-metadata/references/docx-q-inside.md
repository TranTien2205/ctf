# what's embedded from a Office docx

**File:** Office docx — docProps/core.xml+app.xml inside the zip, comments, revisions.

**Question:** what's embedded — embedded files/objects.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
