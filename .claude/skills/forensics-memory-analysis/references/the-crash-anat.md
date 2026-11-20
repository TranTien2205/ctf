# crashdump.py output — anatomy

- Signature PAGE+DU64 (or MDMP for minidump).
- BugCheckCode + 4 parameters — the crash cause.
- MachineType — architecture.
- DirectoryTableBase — the page table root.
- PfnDataBase, PsLoadedModuleList, PsActiveProcessHead — kernel roots.
The header alone often answers "why did it crash".
