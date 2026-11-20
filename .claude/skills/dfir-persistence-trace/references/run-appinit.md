# Registry autostart: AppInit_DLLs

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`Microsoft\Windows NT\CurrentVersion\Windows` values `AppInit_DLLs` (DLL list), `LoadAppInit_DLLs`=1 gate, `RequireSignedAppInit_DLLs`. INERT under Secure Boot since Windows 8 (Microsoft Learn)  -  read LoadAppInit_DLLs and the build first: the value can sit there and never load. Loads into every process that imports user32.dll.

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
