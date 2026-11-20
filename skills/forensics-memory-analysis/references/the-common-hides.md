# Where the flag actually hides

- A late, lone process's memory — memmap it.
- A file it had open — filescan → dumpfiles.
- Its command line — cmdline.
- The console history — consoles/cmdscan.
- The clipboard — clipboard.
- A registry value — printkey.
- Injected code — malfind region.
- A stored credential — hashdump/lsadump.
After dumping, ioc_scan --pattern 'flag\{' finds the token.
