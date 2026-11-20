# Registry autostart: AMSI provider hijack

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`Microsoft\AMSI\Providers\{GUID}` plus `Classes\CLSID\{GUID}\InprocServer32`  -  every AMSI client loads the provider. A medium-integrity process resolves the CLSID from HKCU before HKLM, so an HKCU InprocServer32 pointing at a MISSING DLL is itself the bypass (SpecterOps, Bypassing AMSI via COM Server Hijacking; SigmaHQ registry_set_amsi_com_hijack.yml).

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
