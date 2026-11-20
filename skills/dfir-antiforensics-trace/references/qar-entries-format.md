# Quarantine/MPLog: Entries file format

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Three separately RC4-encrypted sections (Fox-IT, Reverse Reveal Recover): header 60 bytes — `MagicHeader[4]`, `Unknown[4]`, `_Padding[32]`, `Section1Size`, `Section2Size`, `Section1CRC`, `Section2CRC`, `MagicFooter[4]`; section 1 — `Id[16]`, `ScanId[16]`, `Timestamp`, `ThreatId`, `One`, `DetectionName`; section 2 — `EntryCount` then `EntryOffsets[]`, each resource giving `DetectionPath`, `FieldCount`, `DetectionType`, field ids `PhysicalPath` 0x0C, `DetectionContext` 0x0D, `CreationTime` 0x0F, `LastAccessTime` 0x10, `LastWriteTime` 0x11. ERNW's independent table puts the header at 0x3C bytes with data1 length at 0x28 and data2 at 0x2C — two layouts exist, verify which your sample matches before carving.

## Evidence rule

A carved quarantine payload needs its own record: the decryption was run,
the carved offset named, and the hash computed from the carved bytes — quote
the hash output line.

## Pivot

Quarantine empty -> MPLog still names paths Defender touched; then 1116/1117
events if the channel survived.
