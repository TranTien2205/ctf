# ID3 — the audio tags

ID3v1 (last 128 bytes) + ID3v2 (front) — title/artist/comment/
APIC art/private frames. meta_read.py parses v2; the comment and
private frames hide the flag.
