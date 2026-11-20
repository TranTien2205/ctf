# Registry autostart: HKLM Run/RunOnce

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

SOFTWARE `Microsoft\Windows\CurrentVersion\Run` and `...\RunOnce`  -  values are name->command-line, loaded by `explorer.exe` at logon. RunOnce values are DELETED after one run  -  a RunOnce entry that's gone may have fired already; the $J/hive evidence is what's left. Wow6432Node twin for 32-bit views.

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
