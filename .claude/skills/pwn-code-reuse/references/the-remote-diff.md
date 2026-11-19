# Remote vs local — the differences


- Different libc: the remote offsets differ — re-derive.
- Different stack layout: the offsets to buffers differ.
- A wrapper/launcher: the process model differs (fork-server vs
  single-shot).
- ASLR on: always — the leak is mandatory.

## The rule

Verify the chain's assumptions against the remote, not the local
build.
