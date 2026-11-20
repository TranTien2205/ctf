# The memory-analysis workflow — profile first

A memory image is the handout (`*.raw`, `*.vmem`, `*.mem`, `*.dmp`,
hiberfil). The answer is what the machine was doing: a running
process, a typed command, an open file, a password in memory,
injected code.

## The order

1. Identify the image: `vol -f mem.raw windows.info` (or `banners`
   on Linux). A wrong-profile pslist produces garbage that LOOKS
   like a process list — this step validates the whole session.
2. `pslist`/`pstree` — the odd process names the suspect.
3. `cmdline`, `netscan`, `filescan` — what it ran, talked to, opened.
4. `memmap`/`dumpfiles`/`procdump` on the suspect — the flag is
   usually in the process's own memory or its open file.
5. `malfind`/`hivescan` only after a process lead exists.

## No volatility?

    python3 tools/forensics/crashdump.py mem.dmp     # header + bugcheck
    python3 tools/forensics/ioc_scan.py mem.dmp --utf16

crashdump reads the PAGE/DU64 header (bugcheck code + params, DTB,
PsActiveProcessHead); ioc_scan extracts strings/paths/URLs/flag
tokens with byte offsets.
