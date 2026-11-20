# Day zero — no EVTX parser

`xxd -l 8 Security.evtx` prints `ElfFile.`; `strings -el` works
(UTF-16LE, uncompressed event data). Record signature
`\x2a\x2a\x00\x00`, size u32, id u64, FILETIME at 16, binXML at
24 — enough to count records and read timestamps, not `Data Name`.

## The walk

ElfFile. -> ElfChnk -> **\x00\x00 records; timestamps readable.

## The walk

Count records + timestamps without templates.
