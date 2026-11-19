# Code-reuse troubleshooting — the walls


| Symptom | Likely cause | Move |
|---|---|---|
| movaps crash in libc | stack misalignment | insert a bare ret |
| call goes to garbage | wrong libc offset | re-identify the version |
| chain truncated | a bad byte | clean-address gadgets |
| rip walks then dies | a gadget's side effect | audit the full tail |
| nothing happens after ret | dead call slot | pick a firing target |
| leak value looks like stack not libc | wrong field read | the unsorted/GOT entry |
| second stage never runs | no re-entry | single-stage or pivot |
| "no such file" from system | /bin/sh missing | plant it in .bss |
| the chain works locally, not remote | different libc | re-derive remote offsets |
| gadgets exist but can't express the call | the wrong call chosen | ret2csu or a different target |
