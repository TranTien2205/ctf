# The Linux method

1. banners → the kernel + needed ISF symbols.
2. linux.pslist → tasks.
3. linux.bash → command history (often the flag).
4. linux.lsof → open files.
5. linux.netstat → connections.
6. linux.malfind → suspicious mappings.
The blocker is usually missing ISF symbols — ioc_scan/strings is
the fallback.
