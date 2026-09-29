---
name: dfir-persistence-trace
description: >
  Action-oriented depth skill for Host persistence trace. Use after the router or tools/classify.py
  names this class; start with the first probe and record the expected signal. Do not
  use it as proof of a finding. Confusable classes: dfir-execution-trace, dfir-antiforensics-trace.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [dfir, forensics, registry, scheduled-tasks, autostart, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same artifact family: 3 attempts with no new record"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Host persistence trace

**Catalogue class.** Nothing here has solved one: published knowledge, not local experience - record
what actually happens in `field-notes.md`. The wordings that land here - "how did the attacker maintain
access", "what runs at startup", "name the service or task created", "which registry key was modified",
"full path of the binary run at logon" - all ask *how did it survive a reboot or a logoff*, answered as
a value name, a full path, an XML `<Command>` or a unit file.

## First probe

```bash
python3 tools/forensics/evtx_query.py --input system.jsonl --event-id 7045 \
  --order asc --class dfir-persistence-trace --evidence-kind class \
  --challenge <sherlock>-q1 --answer ImagePath
```

7045 on `System` carries `ServiceName`, `ImagePath`, `ServiceType`, `StartType` and `AccountName`; the
SCM writes it with no audit policy needed, so it is almost always there, and `--answer` prints the
`pre-flag` argv. Leave the verdict at its default `inconclusive`; add `--on-match confirms` only once
one of Microsoft's own 4697 triage rules fires - `ImagePath` outside `%windir%` and `Program Files` /
`Program Files (x86)`, `ServiceType` `0x1`/`0x2`/`0x8` (a driver), or `AccountName` none of
`localSystem` / `localService` / `networkService` (Microsoft Learn, 4697).

**Falsifier** - the observation that closes this class: no 7045 on `System`, no 4697 on `Security`, no
non-Microsoft XML under `C:\Windows\System32\Tasks`, and all four Run keys plus `Winlogon\Shell` /
`Winlogon\Userinit` at their defaults (`explorer.exe`, `C:\Windows\system32\userinit.exe,`). Then route to `../dfir-execution-trace/`.

## Confirm

1. `python3 tools/forensics/artifact_inventory.py --path <bundle> --challenge <c>` - are hives, `System.evtx`, `Tasks\`, `OBJECTS.DATA` or a Linux rootfs even present.
2. Quote the mechanism's own record - `ImagePath` out of 7045, the `<Command>` line out of the task XML, the `Debugger` / `Userinit` / `Run` value data out of the hive, or `CommandLineTemplate` out of the WMI consumer. "A new service exists" is `--evidence-kind surface`; `ImagePath=C:\Users\Public\svc.exe` is not.
3. Corroborate the *time* from a second artifact: a registry key carries one timestamp, a task XML carries registration and not execution.

## Registry autostart - full paths, and the one reader on this box today

`regripper`, `reglookup`, `hivexsh` and the `regipy` module are on the absent list at
`../dfir-sherlock-triage/toolchain.md:31`; `regfexport` and `rip.pl` were `command -v`-checked here and are
absent too. Present instead, and run here: impacket's hive CLI at
`/usr/share/doc/python3-impacket/examples/registry-read.py`, banner `Impacket v0.14.0.dev0`, subcommands
`enum_key`/`enum_values`/`get_value`/`get_class`/`walk`, each taking one flag, `-name`.

```bash
R=/usr/share/doc/python3-impacket/examples/registry-read.py
cp SOFTWARE ./SOFTWARE.rw && chmod u+w ./SOFTWARE.rw    # the parser opens 'r+b'
python3 "$R" ./SOFTWARE.rw enum_values -name 'Microsoft\Windows\CurrentVersion\Run'
python3 "$R" ./SYSTEM.rw   get_value   -name 'Select\Current'   # never assume ControlSet001
```

A hive's root **is** its mount point, so `-name` drops the hive name: `SOFTWARE` root is `HKLM\SOFTWARE`,
`SYSTEM` root `HKLM\SYSTEM`, `NTUSER.DAT` root `HKCU`. Replay `LOG1`/`LOG2` first - `../dfir-sherlock-triage/registry-and-execution.md:10-32`.

| Mechanism | Hive and `-name` key | Value | Loaded by |
|---|---|---|---|
| Run / RunOnce, HKLM | `Microsoft\Windows\CurrentVersion\Run`, `...\RunOnce` | any | `explorer.exe` at logon; RunOnce values are deleted after one run |
| Run / RunOnce, HKCU | NTUSER.DAT `Software\Microsoft\Windows\CurrentVersion\Run`, `...\RunOnce` | any | that user's `explorer.exe` |
| RunOnceEx | `Microsoft\Windows\CurrentVersion\RunOnceEx\<NNNN>` plus a `Depend` subkey of DLL paths | any | `runonce.exe` (MITRE T1547.001; the `Depend` loader is UNVERIFIED here) |
| Policies Run, Windows Load | `Microsoft\Windows\CurrentVersion\Policies\Explorer\Run` + HKCU twin; NTUSER.DAT `Software\Microsoft\Windows NT\CurrentVersion\Windows` | any; `Load`, `Run` | `explorer.exe`; `userinit.exe` |
| Winlogon | `Microsoft\Windows NT\CurrentVersion\Winlogon` (also `Wow6432Node`, also HKCU twin) | `Shell`, `Userinit`, `Notify` | `winlogon.exe` (MITRE T1547.004) |
| AppInit_DLLs | `Microsoft\Windows NT\CurrentVersion\Windows` | `AppInit_DLLs`, `LoadAppInit_DLLs`=1, `RequireSignedAppInit_DLLs` | `user32.dll`, into every process that loads it |
| AppCertDlls, BootExecute | SYSTEM `<set>\Control\Session Manager\AppCertDlls`; SYSTEM `<set>\Control\Session Manager` | any; `BootExecute`, default `autocheck autochk *` | every `CreateProcess` caller; `smss.exe` before any service |
| IFEO | `Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<exe>` | `Debugger` (and `<exe>` never runs); or `VerifierDlls` plus `GlobalFlag`=0x100 (`FLG_APPLICATION_VERIFIER`, Microsoft Learn) | the launcher of `<exe>`; the loader, as Application Verifier |
| SilentProcessExit | `Microsoft\Windows NT\CurrentVersion\SilentProcessExit\<exe>` | `ReportingMode`=0x1 (`LAUNCH_MONITORPROCESS`; 0x2 dump, 0x4 notify), `MonitorProcess` (takes `%e` exiting PID, `%i` initiating PID) | the IFEO twin needs `GlobalFlag`=0x200/512, `FLG_MONITOR_SILENT_PROCESS_EXIT` (Microsoft Learn, registry-entries-for-silent-process-exit + enable-silent-process-exit-monitoring). The monitor writes an `Application`-log entry with Source `Process Exit Monitor`; the `WerFault.exe` parentage is UNVERIFIED here |
| COM hijack | NTUSER.DAT `Software\Classes\CLSID\{GUID}\InprocServer32` (also `LocalServer32`, `TreatAs`) | default value = DLL, `ThreadingModel` | any COM client; the HKCU class wins over the HKLM one (MITRE T1546.015) |
| ScreenSaver | NTUSER.DAT `Control Panel\Desktop` | `SCRNSAVE.exe`, `ScreenSaveActive`=1, `ScreenSaverIsSecure`=0, `ScreenSaveTimeout` | `winlogon.exe` after idle (MITRE T1546.002) |
| LSA packages | SYSTEM `<set>\Control\Lsa`, and `Lsa\OSConfig` | `Security Packages`, `Authentication Packages`, `Notification Packages` | `lsass.exe`; the DLL must sit in `C:\Windows\System32` (MITRE T1547.005, T1556.002) |
| Netsh helper | `Microsoft\Netsh` | value name = alias, data = DLL | `netsh.exe` (MITRE T1546.007) |
| Print monitor / Time provider | SYSTEM `<set>\Control\Print\Monitors\<name>`; SYSTEM `<set>\Services\W32Time\TimeProviders\<name>` | `Driver` = full DLL path; `DllName` + `Enabled`=1 | `spoolsv.exe` as SYSTEM at boot (MITRE T1547.010); W32Time as LOCAL SERVICE (T1547.003) |
| AMSI provider | `Microsoft\AMSI\Providers\{GUID}` plus `Classes\CLSID\{GUID}\InprocServer32` | default value = DLL | every AMSI client. A medium-integrity process resolves the CLSID from HKCU before HKLM, so an HKCU `InprocServer32` pointing at a missing DLL is itself the bypass (SpecterOps, *Bypassing AMSI via COM Server Hijacking*; SigmaHQ `registry_set_amsi_com_hijack.yml`) |

## Services and scheduled tasks

Service key: SYSTEM `<set>\Services\<name>` - `ImagePath`, `Type`, `ObjectName`, and
`Parameters\ServiceDll` when the host is `svchost.exe`. `Start` decides reboot survival:
**0** boot, **1** system, **2** auto, **3** manual, **4** disabled (Microsoft Learn, 4697); only 0-2 persist across a reboot.

| Record | Channel | Fields that answer |
|---|---|---|
| 7045 | System | `ServiceName`, `ImagePath`, `ServiceType` (hex: `0x1` kernel driver, `0x10` own process, `0x20` share process), `StartType` (**a string**, not the 0-4 integer; spelled `autostart` in the Psmths sample, other spellings UNVERIFIED here), `AccountName` |
| 4697 | Security | `ServiceName`, `ServiceFileName`, `ServiceStartType` (**numeric** 0-4), `ServiceAccount`, `SubjectUserName` |
| 7034 / 7036 / 7040 | System | crashed / state change / start type changed |

The two field sets differ: a 4697 record has no `ImagePath`. 4697 also needs the *Audit Security System Extension* subcategory on (Microsoft Learn, 4697), so its absence proves nothing.

Tasks live in two places answering different questions. `C:\Windows\System32\Tasks\<folder>\<name>` is XML
with no extension holding `<Command>`, `<Arguments>`, `<UserId>`, `<LogonType>`, `<Triggers>`, `<Hidden>`,
`<Author>` and `<Date>` (registration) - the payload command is here:
`grep -rl '<Command>' Tasks/ | xargs grep -h -A1 '<Command>'`. SOFTWARE
`Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\<path>` carries value `Id`, the task GUID;
`...\TaskCache\Tasks\{GUID}` carries `Path`, `Actions` and `Triggers` (binary blobs), `DynamicInfo`, `Hash`,
and `SecurityDescriptor` in SDDL - which is what still answers *which account* once the XML is deleted
(libyal winreg-kb *Task scheduler*; artefacts.help *Registry - Scheduled tasks*). Both give the sibling
subkeys as `Boot`, `Logon` and `Plain`, each holding only an `Id` back into `Tasks`; a `Maintenance`
subkey and a `URI` value are UNVERIFIED here.

**Last run time lives in the `DynamicInfo` binary value and nowhere else in the registry** (cyber.wtf,
"Windows Registry Analysis - Tasks"): `magic` DWORD at offset 0 (currently 0x3), `ftCreate` FILETIME at
4, `ftLastRun` at 12, `dwTaskState` DWORD at 20, `dwLastErrorCode` DWORD at 24, `ftLastSuccessfulRun`
at 28 - absent on Vista/7, so the blob is 28 or 36 bytes. libyal winreg-kb *Task scheduler* corroborates
the same offsets and split independently. No parser here, so decode it - this ran on a synthetic blob:

```bash
python3 -c "
import sys,struct,datetime;b=open(sys.argv[1],'rb').read()
f=lambda o:(datetime.datetime(1601,1,1)+datetime.timedelta(microseconds=struct.unpack_from('<Q',b,o)[0]//10)).isoformat()
print(len(b),'create',f(4),'lastrun',f(12),'state',struct.unpack_from('<I',b,20)[0],
      'err',hex(struct.unpack_from('<I',b,24)[0]),'lastok',f(28) if len(b)>=36 else 'absent')" dynamicinfo.bin
```

**Why 4698 alone cannot answer "when did it execute".** 4698 is *A scheduled task was created*:
registration only, with the XML in `TaskContent`. Execution is `TaskScheduler/Operational` **200** action
started, **201** action completed, **129** created task process (it names the spawned process), or
`DynamicInfo` offset 12. Change records: Security **4698** created, **4699** deleted, **4700** enabled,
**4701** disabled, **4702** updated; Operational **106** registered, **140** updated, **141** deleted. A
task created, run once and deleted leaves 4698, 4699 and a 141 with no XML on disk.

## WMI subscription, startup folders, Office and BITS

A WMI permanent subscription is three objects and fires only if all three exist: `__EventFilter` (the WQL
trigger), an `__EventConsumer` subclass - `CommandLineEventConsumer` (`CommandLineTemplate`) or
`ActiveScriptEventConsumer` (`ScriptText`) - and `__FilterToConsumerBinding` joining them. On disk they
serialise into `C:\Windows\System32\wbem\Repository\OBJECTS.DATA`, which needs `INDEX.BTR` and `MAPPING*.MAP`
beside it (SANS, *Finding Evil WMI Event Consumers with Disk Forensics*). No parser here, so day zero is
`strings -a -n 8 OBJECTS.DATA | grep -iE 'EventFilter|EventConsumer|FilterToConsumer|SELECT .* FROM __Instance'`.
In logs: Sysmon **19** filter, **20** consumer, **21** binding
(`../dfir-sherlock-triage/windows-event-logs.md:119-145`); `Microsoft-Windows-WMI-Activity/Operational`
**5861** `Operation_ESStoConsumerBinding` - the binding itself, so this is the record that names the
persistence - **5860** `Operation_TemporaryEssStarted`, **5857** `Operation_Started` (provider loaded),
**5858** `Operation_ClientFailure`, carrying the failing WQL and result code (repnz/etw-providers-docs,
`Microsoft-Windows-WMI-Activity.xml`). Remote execution, same stack: `../ctf-forensics/windows.md:373-392`.

| Mechanism | Path | Read it with |
|---|---|---|
| Startup folders | `C:\Users\<u>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` and `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp` | `ls -la`; for `*.lnk`, `strings -a -el` gives target, volume serial and target MAC times (`lnkinfo` absent here) |
| Office add-in, template | `%APPDATA%\Microsoft\Word\STARTUP\*.wll` (MITRE T1137.006), `%APPDATA%\Microsoft\Excel\XLSTART\*.xll` and `*.xlam`, `%APPDATA%\Microsoft\Templates\Normal.dotm` | `ls -la`; then `python3 -c "import olefile,sys;print(olefile.OleFileIO(sys.argv[1]).listdir())" Normal.dotm` - `olefile` imports here, `oletools` is absent |
| Office COM add-in | HKCU or HKLM `Software\Microsoft\Office\<app>\Addins\<name>`, `LoadBehavior`=3 | `registry-read.py ... enum_values` |
| BITS | queue `C:\ProgramData\Microsoft\Network\Downloader\qmgr.db` (ESE; `esedbexport` measured absent here); log `Microsoft-Windows-Bits-Client/Operational`: **3** BITS Job Created (`Job ID`, job name, `Process Path`, `Owner`), **59** Job Started/Resumed and **60** Job Stopped - 59 and 60 carry the transfer URL - **4** BITS Job Completed. 61 is UNVERIFIED here | `strings -a -el qmgr.db \| grep -iE 'http\|\.exe'`; `evtx_query.py --event-id 3` |

## Linux, and macOS in one table

| Mechanism | Path, in precedence order where it matters | Read it with |
|---|---|---|
| systemd system unit | `/etc/systemd/system/` beats `/run/systemd/system/` beats `/usr/local/lib/systemd/system/` beats `/usr/lib/systemd/system/`; `.d/*.conf` drop-ins merge (`man 5 systemd.unit`, verified here) | `grep -rHE '^(ExecStart\|ExecStartPre\|Environment)=' /etc/systemd/system /usr/lib/systemd/system` |
| systemd user unit | `~/.config/systemd/user/` beats `/etc/systemd/user/` beats `~/.local/share/systemd/user/` beats `/usr/lib/systemd/user/` | the same grep on those four |
| systemd timer | `*.timer` beside the unit, with `OnCalendar=` or `OnBootSec=` and `Unit=` | `grep -rHE 'OnCalendar\|OnBootSec\|^Unit=' --include='*.timer' /etc /usr/lib` |
| systemd generator | `/run/systemd/system-generators/`, `/etc/systemd/system-generators/`, `/usr/local/lib/systemd/system-generators/`, `/usr/lib/systemd/system-generators/` - executables that run **before** units load (`man 7 systemd.generator`, verified here) | `ls -la` on all four |
| cron | `/var/spool/cron/crontabs/<user>` on Debian, command in field 6; `/etc/crontab` and `/etc/cron.d/*` carry a **user field** before the command (`man 5 crontab`, verified here); `/etc/cron.{hourly,daily,weekly,monthly}` are run-parts directories | `grep -rHv '^#' /etc/crontab /etc/cron.d` then `ls -la /etc/cron.*` |
| SSH key, preload | `~/.ssh/authorized_keys`, `~/.ssh/authorized_keys2`; `/etc/ld.so.preload` - **measured absent on this box**, so its mere existence is the finding - and `Environment=LD_PRELOAD=` inside a unit | `cat` both; the key comment often names the operator |
| shell rc | `~/.bashrc`, `~/.bash_profile`, `~/.profile`, `~/.bash_logout`, `/etc/profile`, `/etc/profile.d/*.sh` | `grep -rn 'curl\|wget\|base64\|/dev/tcp' <those paths>` |
| sysvinit and xdg | `/etc/rc.local`, `/etc/init.d/*`, `/etc/rc?.d/S*`; `/etc/xdg/autostart/*.desktop`, `~/.config/autostart/*.desktop` | `ls -la`, then `grep -H '^Exec=' <the .desktop files>` |
| where the change is recorded | auditd `/var/log/audit/audit.log` (`type=SYSCALL` joined to `type=PATH name="/etc/cron.d/..."`), `journalctl -u <unit>`, `CRON[` lines in `/var/log/syslog` | `grep -F '/etc/cron.d' /var/log/audit/audit.log` |
| macOS | `/Library/LaunchDaemons/*.plist` (root, at boot), `/Library/LaunchAgents`, `~/Library/LaunchAgents`, `/System/Library/Launch{Agents,Daemons}`; keys `Label`, `ProgramArguments`, `RunAtLoad`, `StartInterval` (MITRE T1543.001). Login items: `~/Library/Application Support/com.apple.backgroundtaskmanagementagent/BackgroundItems-v*.btm`, layout UNVERIFIED here | `python3 -c "import plistlib,sys;print(plistlib.load(open(sys.argv[1],'rb')))" <f>.plist`; `strings -a` for the btm |

## Traps

- **`Start`=3 or 4 is not reboot persistence.** Something else started that service, and that something is the real answer. And **Winlogon `Notify` is an XP/2003 mechanism**: post-Vista `winlogon.exe` no longer loads notification package DLLs, so a `Notify` value is probably stale (UNVERIFIED here).
- **`AppInit_DLLs` is inert when Secure Boot is on.** Microsoft Learn, *AppInit DLLs and Secure Boot*: "Starting in Windows 8, the AppInit_DLLs infrastructure is disabled when secure boot is enabled." The value sits in the hive and never loads; read `LoadAppInit_DLLs` and the build (SOFTWARE `Microsoft\Windows NT\CurrentVersion`, values `CurrentBuild` and `ProductName`) first. And **a registry key has exactly one timestamp**, `lastChange` on the key and not per value, so a Run key with five values dates only the newest write.
- **The parser opens the hive read-write.** `impacket/winregistry.py:209` calls `open(hive,'r+b')`; a read-only evidence copy raises `PermissionError: [Errno 13]` (measured here on a `chmod 444` file). Copy, then `chmod u+w`.
- **A non-hive file and a truncated hive fail at different depths, and neither message names the file.** Measured here on v0.14.0.dev0: 8 KB of `/dev/urandom` raises `ValueError: Could not determine registry hive format (not a binary hive or export)` from `winregistry.py:808`; a 4-byte `regf` stub gets past that sniff and dies as `struct.error: unpack requires a buffer of 4 bytes` in `impacket/structure.py`. Check first: `head -c4 SOFTWARE` must print `regf`.
- **Repointing an existing task leaves 4702, not 4698**, and the XML `<Date>` still shows the original registration; a `<Date>` far from `DynamicInfo` `ftCreate` is timestomping - `../ctf-forensics/windows.md:294-316`.
- **Prefetch proves the payload ran, not that the mechanism fired.** Read the mechanism off the parent alone: `svchost.exe -k netsvcs`, `taskeng.exe`, `WerFault.exe`, `wmiprvse.exe` (Sysmon 1 `ParentImage`, or `TaskScheduler/Operational` 129).
- **After a 1102**, task XML creation still shows in `$J` - `../ctf-forensics/windows.md:318-354`; checklist at `:481-498`.

## Routing

Shares signals with `../dfir-execution-trace/` (what ran, once) and `../dfir-antiforensics-trace/`
(the mechanism was removed or timestomped); check both first. Not this file when the question is *who
authenticated* - `../dfir-authentication-trace/`. Router: `../dfir-sherlock-triage/method.md`. Already
written, do not restate: `../dfir-sherlock-triage/registry-and-execution.md`, `../ctf-forensics/linux-forensics.md:42-64`,
`../dfir-sherlock-triage/windows-event-logs.md:173-189`.

## Discipline

One mechanism family per probe. Three reads of one family with no new record and the budget says pivot to
the next family in the tables above, never another value in the same key. One axis before "which came first":

```bash
python3 tools/forensics/timeline_merge.py --source tasks.csv:Date:task \
  --source svc.csv:TimeCreated:svc7045 --source runkeys.csv:lastChange:runkey \
  --challenge <sherlock> --gap 600
```

Format, timezone and precision: `../dfir-sherlock-triage/answer-discipline.md`. Every verdict through
`tools/hooks.py post-probe`; no quoted payload path means `--evidence-kind surface`, which cannot confirm.
