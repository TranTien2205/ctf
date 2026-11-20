# carve_scan.py — appended/embedded scan

    python3 tools/forensics/carve_scan.py <file>
    python3 tools/forensics/carve_scan.py <file> --extract out/

Embedded-file magic + trailing-data scan — finds the archive
appended after the image's end marker.
