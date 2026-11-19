# The traps table — every way chains die — map

Companion to `the-traps-table.md`.

| Trap | Symptom | Fix |
|---|---|---|
| misaligned rsp at call | movaps crash | insert a ret |
| wrong libc offsets | garbage call | re-identify the version |
| bad byte in an address | truncated payload | pick a clean gadget |
| stale leak | wrong base | re-leak per run |
| missing pop rdx | arg unset | substitute gadget |
| GOT read too early | resolver stub not libc | call the import first |
| gadget side-effect | state clobbered | audit the full tail |
| one-shot with a 2-stage chain | no re-entry | pivot or compress |
| PIE without leak | addresses unknown | leak a code ptr first |
| canary unplaced | abort before ret | leak and place it |
