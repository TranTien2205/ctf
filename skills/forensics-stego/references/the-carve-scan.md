# carve_scan.py — the stdlib scan

The absent-binwalk fallback: embedded magics + trailing data past a
container's real end + a flag-format pass over printable runs.

## The call

    python3 tools/forensics/carve_scan.py f.png
    python3 tools/forensics/carve_scan.py f.png --extract out/
