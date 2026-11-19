# The mistakes table — every error and its fix


| Mistake | Symptom | Fix |
|---|---|---|
| wrong arg offset N | marker absent / wrong value | re-scan the offset |
| mixed %N$ and % | glibc error | all-positional or all-walk |
| count arithmetic off | wrong byte written | recompute cumulative |
| pointer misaligned | write to wrong addr | pad to 8-byte boundary |
| full RELRO GOT write | crash | ret-addr/hook instead |
| %s on unmapped | crash | that arg isn't a pointer |
| no arg plant position | can't reach target | two-stage write |
| truncated leak | partial dump | fewer specifiers per call |
| stale leak reused | wrong address | re-leak per call |
| forgot the redirect | write lands, nothing fires | pick a firing slot |
