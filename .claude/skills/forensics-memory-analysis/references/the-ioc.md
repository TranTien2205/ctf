# ioc_scan.py — strings and IOCs

    python3 tools/forensics/ioc_scan.py mem.dmp --utf16
    ioc_scan.py mem.dmp --pattern 'flag\{'

Strings + paths + URLs + flag tokens with byte offsets; --utf16
for wide strings, --min for length, --strings-only for raw list.
