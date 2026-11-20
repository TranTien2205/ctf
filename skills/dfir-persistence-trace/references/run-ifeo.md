# Registry autostart: IFEO Debugger

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`Image File Execution Options\<exe>` values `Debugger` (the named exe NEVER runs  -  the debugger launches instead, receiving the original command line) or `VerifierDlls` plus `GlobalFlag`=0x100 (FLG_APPLICATION_VERIFIER). The Debugger form is the classic; a Debugger on `sethc.exe`/`utilman.exe`/`osk.exe`/`magnify.exe`/`narrator.exe` is also the sticky-keys backdoor pattern.

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
