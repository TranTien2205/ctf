# crashdump.py — the no-volatility route

    python3 tools/forensics/crashdump.py mem.dmp

Reads the PAGE/DU64 header: bugcheck code + 4 params ("why it
crashed"), machine type, DTB, PFN database, PsLoadedModuleList,
PsActiveProcessHead; recognizes minidumps (MDMP). Content
extraction then falls back to ioc_scan.
