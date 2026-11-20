# The checklist

- [ ] Image format + OS profile identified (windows.info/banners)
- [ ] pslist/pstree — suspect named
- [ ] cmdline/netscan/filescan triage
- [ ] memmap/procdump/dumpfiles on the suspect
- [ ] ioc_scan/strings on the dump for the flag
- [ ] malfind/ldrmodules checked if no lead surfaced
- [ ] hashdump/lsadump/clipboard/consoles for creds
- [ ] UTF-16 strings not forgotten (--utf16)
- [ ] Every finding tied to a plugin output row + offset
- [ ] Clean workload recorded as a negative if so
- [ ] Flag through the hook
