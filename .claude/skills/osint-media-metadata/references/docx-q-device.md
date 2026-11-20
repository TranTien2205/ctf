# on what device from a Office docx

**File:** Office docx — docProps/core.xml+app.xml inside the zip, comments, revisions.

**Question:** on what device — the camera/software string.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
