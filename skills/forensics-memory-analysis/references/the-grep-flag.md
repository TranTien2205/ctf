# Hunting the flag token — the direct route

    python3 tools/forensics/ioc_scan.py mem.dmp --pattern 'flag\{'
    strings -a mem.dmp | grep -i flag

When the flag is a literal string in memory, this alone works —
before any plugin walk.
