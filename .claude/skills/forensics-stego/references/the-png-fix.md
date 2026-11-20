# png_fix.py — the repair

Rewrites CRCs, drops non-chunk bytes, appends IEND — a tampered
chunk is a signal, not just damage; never invents pixel data.
