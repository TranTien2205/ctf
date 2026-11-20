# The Windows method — full

1. windows.info → profile.
2. pslist + psscan + pstree → the suspect.
3. cmdline + envars + netscan + filescan → context.
4. memmap/procdump/dumpfiles → extract.
5. malfind + ldrmodules + apihooks → injected code.
6. hivescan/printkey → registry.
7. hashdump/lsadump → creds.
8. ioc_scan/strings on dumps → the flag.
