# Heap troubleshooting — the common walls — map

Companion to `troubleshoot.md`.

| Symptom | Likely cause | Move |
|---|---|---|
| "double free detected" | tcache key (2.29+) | clear key or A-B-A order |
| fd aim returns garbage | safe-linking (2.32+) | leak pos, write mangled |
| alloc returns a different addr | wrong bin expectation | re-check size class/routing |
| corrupted top size abort | house-of-force check | different write route |
| crash in _int_malloc | corruption already done | break earlier, dmh the state |
| leak gives stack not libc | wrong field read | unsorted fd is the libc one |
| second alloc same addr "works" but no effect | overlap into non-pointer | pick a pointer-bearing object |
| hooks write does nothing | glibc >= 2.35 | FSOP / app pointers |
| fake chunk rejected | next-size check | forge both size fields |
| everything worked locally, remote dies | different libc/version | re-leak against the remote libc |
