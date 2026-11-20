# Appended data — after the end marker

Data appended after the format's end marker (JPEG FFD9, PNG IEND)
— a hidden archive or second file. carve_scan.py finds it;
binwalk -e extracts; strings surface embedded tokens.
