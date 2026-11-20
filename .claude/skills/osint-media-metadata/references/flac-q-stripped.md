# is it stripped from a FLAC audio

**File:** FLAC audio — Vorbis comments + pictures.

**Question:** is it stripped — metadata wiped on upload.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
