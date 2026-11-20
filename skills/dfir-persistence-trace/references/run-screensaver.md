# Registry autostart: ScreenSaver

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

NTUSER.DAT `Control Panel\Desktop`: `SCRNSAVE.exe` names the screensaver binary, `ScreenSaveActive`=1, `ScreenSaverIsSecure`=0 (no lock), `ScreenSaveTimeout`  -  winlogon launches it after idle. A planted SCRNSAVE.exe is persistence triggered by inactivity (T1546.002).

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
