# The final word — memory analysis in one line

A memory image: **identify the profile, name the suspect process,
dump its memory, and hunt the flag token.** The plugin output,
quoted verbatim, is the evidence.

- windows.info/banners first — a wrong profile makes pslist lie.
- pslist tail + psscan + pstree + cmdline name the suspect.
- memmap/procdump/dumpfiles extract; ioc_scan/strings find the flag.
- All-accounted-for normal workload is the falsifier — reclassify.
- crashdump.py + ioc_scan.py are the no-volatility local route.
- Companions: `-deep`, `-checklist`, `-map`, `-index`, `-recap`,
  `-ref`, `-route` per module.

## The decision sequence

1. windows.info/banners → the profile (validates everything).
2. pslist + psscan + pstree → the suspect process.
3. cmdline + envars + netscan + filescan → its context.
4. memmap/procdump/dumpfiles → its bytes.
5. ioc_scan/strings on the dump → the flag token.
6. malfind/ldrmodules/apihooks → injected code, if no lead yet.
7. hashdump/lsadump/clipboard/consoles → creds and typed data.
