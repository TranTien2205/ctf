# is it stripped from a MP4 video

**File:** MP4 video — moov/udta metadata atoms.

**Question:** is it stripped — metadata wiped on upload.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
