# Appended data — the common hide

Bytes after the container's real end are invisible to the format's
reader — the standard cheap hide. carve_scan finds trailing data
past the real end; a zip EOT comment / a PNG post-IEND / a JPEG
post-FFD9.

## The scan

    python3 tools/forensics/carve_scan.py challenge.png
    python3 tools/forensics/carve_scan.py challenge.png --extract out/
