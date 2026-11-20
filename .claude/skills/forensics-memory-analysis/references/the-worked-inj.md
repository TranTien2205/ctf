# Worked — injected shellcode

1. malfind → an RWX unbacked region in a process.
2. Dump the region → ioc_scan/capstone — the flag or a
   second-stage URL inside.

## Notes

- The region's protection (PAGE_EXECUTE_READWRITE) and missing
  file backing are the injection tells.
- ldrmodules on the same PID often shows the discrepancy too —
  cross-confirm before dumping.
- The dumped region is a blob: ioc_scan for strings/URLs, then
  capstone if code bytes look like shellcode.
