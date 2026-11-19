# The walk table — rip's journey


| Step | rip | rsp | action |
|---|---|---|---|
| 0 | ret-from-vuln | saved-rip | the overwrite's ret |
| 1 | gadget 1 | +8 | its instructions |
| 2 | gadget 2 | +8 more | ... |
| n | the call | ... | the callee runs |
| n+1 | the ending | ... | exit/loop |
