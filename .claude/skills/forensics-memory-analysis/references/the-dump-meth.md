# Dumping the suspect — the method

- memmap --pid N --dump → full address space.
- procdump --pid N → the executable image.
- dumpfiles → the files it had open.
Then ioc_scan/strings --utf16 on each for flag{ tokens.
