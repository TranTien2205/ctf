# Registry autostart: SilentProcessExit

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`SilentProcessExit\<exe>`: `ReportingMode`=0x1 (LAUNCH_MONITORPROCESS; 0x2 dump, 0x4 notify), `MonitorProcess` (gets `%e` exiting PID, `%i` initiating PID substituted). Needs the IFEO twin key with `GlobalFlag`=0x200/512 (FLG_MONITOR_SILENT_PROCESS_EXIT). The monitor writes an Application-log entry Source `Process Exit Monitor`; WerFault.exe parentage is UNVERIFIED here.

## Reading it

```bash
R=/usr/share/doc/python3-impacket/examples/registry-read.py
cp SOFTWARE ./SOFTWARE.rw && chmod u+w ./SOFTWARE.rw   # parser opens 'r+b'
python3 "$R" ./SOFTWARE.rw enum_values -name 'Microsoft\Windows\CurrentVersion\Run'
```

Replay `LOG1`/`LOG2` first  -  `skills/dfir-sherlock-triage/registry-and-execution.md:10-32`.

## Evidence rule

Quote the value name AND data verbatim  -  a trimmed display name is not the
record.

## Pivot

Family clean -> tasks (`task-*`), services (`svc-*`), WMI (`wmi-*`).
