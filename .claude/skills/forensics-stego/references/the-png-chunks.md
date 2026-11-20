# PNG chunks — the structural hide

A PNG's chunks — a non-standard ancillary chunk, a bad CRC, bytes
between chunks — img_struct.py lists them with per-chunk CRC checks;
a bad CRC is a tamper signal.

## The repair

    python3 tools/forensics/png_fix.py broken.png --fix out.png

Rewrites CRCs, drops non-chunk bytes, appends missing IEND.
