# Remote vs local — the differences — checklist

Companion to `the-remote-diff.md`.

## Checklist

- [ ] Different libc: the remote offsets differ — re-derive.
- [ ] Different stack layout: the offsets to buffers differ.
- [ ] A wrapper/launcher: the process model differs (fork-server vs
- [ ] ASLR on: always — the leak is mandatory.
