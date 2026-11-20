# what's embedded from a APK package

**File:** APK package — manifest + cert + META-INF.

**Question:** what's embedded — embedded files/objects.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
