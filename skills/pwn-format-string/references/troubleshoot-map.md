# Troubleshooting — symptom → cause → fix — map

Companion to `troubleshoot.md`.

| Symptom | Cause | Fix |
|---|---|---|
| %p prints only 'AAAA' | buffer isn't a printf arg | re-find the arg index |
| AAAA.%N$p never shows 0x41414141 | wrong N or not an arg | scan wider |
| %n writes wrong value | count arithmetic off | recount cumulative bytes |
| the write crashes | bad target addr | check the target's address |
| GOT write lands but no redirect | wrong slot or not called | check which import fires next |
| %s crashes | planted ptr unmapped | the deref is the read |
| chain lands but no flag | wrong flag path/arg | redirect's arg comes from call site |
| byte-write wrong | count's low byte off | recompute the cumulative count |
| blind, no output | no output channel | find a channel or write blind |
