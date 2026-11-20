# Registry autostart: Hive root = mount point

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

registry-read.py `-name` drops the hive prefix: SOFTWARE root is HKLM\SOFTWARE, SYSTEM root HKLM\SYSTEM, NTUSER.DAT root HKCU. So `-name 'Microsoft\Windows\CurrentVersion\Run'`, NOT `-name 'HKLM\SOFTWARE\...'`. A doubled prefix returns a key-not-found that looks like absence.

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
