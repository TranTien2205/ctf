# Goal -> plugin -> one-liner

Profile first. Everything below assumes volatility3 (`vol`), Windows image;
Linux images use `linux.*`/`banners` equivalents.

| Goal | Plugin | Command |
|---|---|---|
| identify image | windows.info | `vol -f mem.raw windows.info` |
| what ran | pslist / pstree | `vol -f mem.raw windows.pslist` |
| with what args | cmdline | `vol -f mem.raw windows.cmdline` |
| talked to whom | netscan | `vol -f mem.raw windows.netscan` |
| files open/on disk | filescan | `vol -f mem.raw windows.filescan \| grep -i flag` |
| dump a file by virt addr | dumpfiles | `vol -f mem.raw windows.dumpfiles --virtaddr 0x...` |
| dump a process | procdump/memmap | `vol -f mem.raw windows.memmap --pid N --dump` |
| injected code | malfind | `vol -f mem.raw windows.malfind` |
| registry content | hivescan/printkey | `vol -f mem.raw windows.printkey --key "..."` |
| browser history | (filescan for History/WAL) | dumpfiles then sqlite3 |
| typed input | (console/cmdscan) | `vol -f mem.raw windows.cmdscan` |

## Hunting the flag, cheap-first

1. `cmdline | grep -v svchost` — the planted process is late, alone, oddly
   named.
2. `filescan | grep -iE 'flag|secret|note'` — the file table keeps the path
   even when the file is deleted on disk.
3. `windows.netscan` — a live CTF process often holds an outbound connection;
   its peer is the next pivot.
4. `memmap --pid <suspect> --dump` then `strings` the dump — flag-shaped text
   sits in process memory for CTF plants.
5. `cmdscan`/consoles — what the operator literally typed.

## Traps

- Wrong profile = plausible garbage. If `pslist` shows nonsense or zero
  processes, STOP — re-identify the image, do not keep hunting.
- `malfind` flags JIT'd code and .NET legitimately — a hollow finding needs
  the dump, not the plugin verdict.
- hiberfil.sys is compressed — `imageinfo` will not read it; use
  volatility's hiberfil support or convert first.
