# Cross-checks — verifying each stage independently


Each fmtstr stage has an independent test — verify them in isolation
before composing.

| Stage | Independent check |
|---|---|
| primitive | %p reflects a pointer |
| offset N | marker at arg N |
| leak | a known value appears (canary slot, code ptr) |
| plant | %N$p prints the planted address |
| write | read-back shows the byte |
| redirect | the import fires / the return happens |

A composed exploit failing at an unknown stage wastes the run — isolate
each stage's signal first.
