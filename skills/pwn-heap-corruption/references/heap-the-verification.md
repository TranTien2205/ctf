# Verifying the heap run — the hard signals


| Stage | The verify |
|---|---|
| UAF | the freed object's fields still respond |
| dup | same address returned to two live slots |
| leak | a range-shaped value (0x55/0x7f/0x7ff) |
| poison | second alloc returns the aimed target |
| overlap | marker round-trip A→B |
| write | the slot's read-back changed |
| redirect | the call/return/free fired |

No verify, no proceed — a heap run is only as strong as its weakest
unverified stage.
