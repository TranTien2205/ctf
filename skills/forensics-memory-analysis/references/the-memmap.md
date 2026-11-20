# memmap / procdump — dumping the suspect

`windows.memmap --pid N --dump` writes the process's address space;
`windows.pslist` + `procdump` dumps the executable image. Then
`strings`/ioc_scan on the dump — the flag is usually in the
process's own memory.
