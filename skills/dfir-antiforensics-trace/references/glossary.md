# Glossary

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

| Term | Meaning here |
|---|---|
| record identifier | EVTX monotonic counter — the gap test's unit |
| record number | per-chunk position — resets, not the gap test |
| ElfChnk | 64KB EVTX chunk; first/last ids at +0x18/+0x20 |
| 1102 | Security-cleared event — timestamp is clear time |
| 104 | non-Security-cleared event — Channel field names the log |
| 1100 | logging service shutdown — pair with 4609 reboot check |
| 4719 | audit policy change event |
| $SI/$FN | $STANDARD_INFORMATION (user-settable) vs $FILE_NAME (kernel) |
| 0x8000 | $J BASIC_INFO_CHANGE — attributes OR timestamps |
| 0x200 | $J FILE_DELETE record |
| $I/$R | $Recycle.Bin metadata/content file pair |
| Sysmon 2 | FileCreateTime — Previous vs Creation pair |
| Sysmon 23/26 | FileDelete archived / not archived |
| Sysmon 28 | FileBlockShredding — names the shredder |
| Sysmon 4/16 | Sysmon service state / config change — unfilterable |
| MPLog | Defender support log surviving Security clears |
| quarantine | RC4-obfuscated store holding deleted payloads |
| USN-0 volume | journal-deleted signature across all MFT records |
| .LOG1/.LOG2 | registry transaction logs — replay BOTH on 8.1+ |
| regf seq | primary/secondary sequence numbers — unequal = dirty hive |
| EFSTMPWP | cipher /w free-space wipe temp file |
| EulaAccepted | SDelete registry key proving it ran |
| AAA.AAA burst | SDelete's 26-rename $J fingerprint |
| clear vs gap | evented erase (1102/104) vs silent record deletion |
| collection scope | absent artifact explained by collection, not tamper |
| recovery table | destroyed-artifact -> surviving-artifact columns |
| claim vs record | a technique name vs the quotable evidence |
