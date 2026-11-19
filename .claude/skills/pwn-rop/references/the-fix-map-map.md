# The fix map — symptom to repair — map

Companion to `the-fix-map.md`.

| Symptom | Repair |
|---|---|
| rip=0x41.. | re-measure the offset |
| movaps crash | insert ret |
| call to garbage | re-derive the libc offset |
| truncated chain | fix the bad byte |
| no leak print | call the import first |
| dead second stage | check the re-entry |
