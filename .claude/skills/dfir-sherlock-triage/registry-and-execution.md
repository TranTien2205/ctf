# Registry and execution artifacts

Answers "what ran, when, how often, and what persisted" from hives, prefetch,
Amcache, shimcache, shellbags and scheduled tasks.

Evidence level: catalogue. Hive paths and artifact semantics are standard published
knowledge. Tool invocations were verified against each tool's own source or README;
confirm against the installed build with `--help`.

## Replay the transaction logs FIRST

A hive captured from a live machine is dirty: the newest writes sit in `LOG1` and
`LOG2`, not in the hive. Reading it without replaying them returns stale values,
silently. This is the single most common way a registry answer comes out wrong.

```bash
regipy-process-transaction-logs NTUSER.DAT \
  -p ntuser.dat.log1 -s ntuser.dat.log2 -o recovered_NTUSER.dat
```

Python form - note the parameter names, which are positional-by-meaning and easy to
get wrong:

```python
from regipy.recovery import apply_transaction_logs
apply_transaction_logs(hive_path, primary_log_path,
                       secondary_log_path=None, restored_hive_path=None)
```

There is **no** `transaction_log_path` parameter; passing one raises `TypeError`.
Verified against `regipy/recovery.py`.

## Hive to question map

| Hive | Holds | Question it answers |
|---|---|---|
| `SYSTEM` | `CurrentControlSet\Services` | what service was installed, its image path and start type |
| `SYSTEM` | `Enum\USBSTOR`, `MountedDevices` | what USB device was attached, when, and what letter it got |
| `SYSTEM` | `Control\ComputerName`, `TimeZoneInformation` | the host name, and **the offset needed to normalise every local timestamp** |
| `SOFTWARE` | `Microsoft\Windows\CurrentVersion\Run`, `RunOnce` | what persisted at logon |
| `SOFTWARE` | `Microsoft\Windows NT\CurrentVersion` | OS build - decides which artifact semantics apply |
| `SAM` | `Domains\Account\Users` | local accounts; key last-write time dates account creation |
| `NTUSER.DAT` | `...\Explorer\UserAssist` | GUI programs run by that user, with a run count |
| `NTUSER.DAT` | `...\Explorer\TypedPaths`, `RunMRU`, `RecentDocs` | what the user typed, ran and opened |
| `NTUSER.DAT` | `...\Explorer\RunMRU` | commands typed into the Run box |
| `UsrClass.dat` | shellbags | folders browsed, including ones now deleted or on removed media |
| `Amcache.hve` | `InventoryApplicationFile` | executed and present binaries, **with a SHA-1** |

`SYSTEM\Control\TimeZoneInformation` is worth reading first on any bundle whose
timestamps are local. It converts a whole set of answers at once.

Two caveats that are caveats, not facts:

- **Shimcache presence is not execution** on all Windows versions. It records that
  the binary was *seen* by the compatibility cache. Do not answer "was it executed"
  from shimcache alone; corroborate with Prefetch or Amcache.
- **`ControlSet001` vs `ControlSet002`.** The live set is named by `Select\Current`.
  regipy's `get_control_sets()` resolves it; guessing `ControlSet001` is wrong often
  enough to matter.

## Reading a hive

```bash
regfexport SOFTWARE                               # libregf-utils, whole-hive export
regfinfo SYSTEM                                   # hive metadata
rip.pl -r NTUSER.DAT -p userassist                # RegRipper, one plugin
rip.pl -r SYSTEM   -p services
rip.pl -r SYSTEM   -p usbstor
rip.pl -r SOFTWARE -p run
```

RegRipper is plugin-driven and is the fastest path to a named question. regipy is
the scriptable counterpart when the answer needs filtering or a join:

```python
from regipy.registry import RegistryHive
from regipy.utils import convert_wintime

hive = RegistryHive("recovered_NTUSER.dat")
sk = hive.get_key(r"\Software\Microsoft\Windows\CurrentVersion\Run")
print(convert_wintime(sk.header.last_modified).isoformat())
for value in sk.get_values():
    print(value.name, value.value)
```

A key's last-write time is frequently the literal answer to a "when did this
persist" question - the key has no other timestamp.

## Prefetch

`C:\Windows\Prefetch\*.pf`. 200+ files in a bundle is normal.

```bash
sccainfo NAME-HASH.pf        # libscca-utils
```

Each `.pf` carries, and these are the three answers it gives:

- **Run count** - "how many times was it executed".
- **The last eight execution timestamps** - not just the most recent. A question
  asking "when was it FIRST run" is often answerable from the oldest of the eight,
  and the file's own creation time dates the first execution ever.
- **The referenced-file list** - every DLL and data file the binary touched in its
  first ten seconds. This is how a loader is tied to its payload.

Prefetch survives log clearing entirely, which makes it the primary fallback after
a 1102. Note it may be disabled on a server build - absence is not evidence.

## Amcache

`C:\Windows\AppCompat\Programs\Amcache.hve`. A registry hive, so the transaction-log
rule above applies.

`InventoryApplicationFile` entries carry the file path, the size, the linking
timestamp and a **SHA-1**. That hash is the pivot when the binary itself is gone:
it matches a carved sample, a Defender quarantine entry, or a threat-intel lookup.

A question asking for SHA-256 cannot be answered from Amcache - it stores SHA-1.
Recover the sample and hash it.

## Scheduled tasks

Two sources, answering different questions:

- `C:\Windows\System32\Tasks\<name>` - XML on disk, carries the full action, the
  trigger and the principal. This is where "what command does the task run" lives.
- `SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree` and
  `\Tasks` - registration and, in `TaskCache\Tasks`, the last-run and next-run times.
- Security 4698 records creation; `TaskScheduler/Operational` 200/201 records each
  actual **execution**, which 4698 does not give.

## Other execution and usage artifacts

| Artifact | Location | Answers |
|---|---|---|
| ShellBags | `UsrClass.dat` | folders browsed, including deleted or removable ones |
| LNK files | `%APPDATA%\Microsoft\Windows\Recent` | original path, volume serial, MAC times of the target |
| Jump Lists | `...\Recent\AutomaticDestinations` | per-application recent items |
| SRUM | `C:\Windows\System32\sru\SRUDB.dat` | **bytes sent per process** - the exfiltration-volume answer when no capture exists |
| Browser history | `places.sqlite`, `History` | downloads, visits; plain SQLite, `sqlite3` is installed |
| Windows Timeline | `ActivitiesCache.db` | which application was in use at a given time; SQLite |
| RMM tool logs | AnyDesk `ad.trace` / `connection_trace.txt`, TeamViewer `connections_incoming.txt` | remote-access initial entry, with source id and time |
| WER reports | `ReportArchive`, `ReportQueue`, `*.wer` | a crashed process: full path and version - often the only trace of a failed payload |

`SRUDB.dat` and `WebCacheV01.dat` are ESE databases:

```bash
esedbexport -t <outdir> SRUDB.dat            # libesedb-utils
```

LNK and Jump List parsing:

```bash
lnkinfo <file>.lnk                            # liblnk-utils
```

SQLite artifacts need no install:

```bash
sqlite3 ActivitiesCache.db ".tables"
sqlite3 History "SELECT datetime(last_visit_time/1000000-11644473600,'unixepoch'), url FROM urls ORDER BY last_visit_time DESC LIMIT 40;"
```

Chromium stores times as microseconds since 1601; the arithmetic above converts to
UTC. Firefox `places.sqlite` uses microseconds since 1970 instead - divide by
1000000 and skip the offset.

## Falsifier

This file is the wrong one when the question is about network behaviour or about
what a process did at runtime rather than what it left behind. Route back through
`method.md` step 1.
