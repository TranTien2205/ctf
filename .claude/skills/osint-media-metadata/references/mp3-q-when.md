# when was it taken from a MP3 audio

**File:** MP3 audio — ID3v1/v2 tags, APIC art, private frames.

**Question:** when was it taken — create/modify/digitize times.

meta_read.py + exiftool -a -u -g1 for the tags; carve_scan.py + strings for appended data. Quote the verbatim field value.
