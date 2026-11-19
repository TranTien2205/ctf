# Bug-to-technique matrix — which recipe fits which bug


| The bug | The primitive | First technique to reach |
|---|---|---|
| UAF (dangling r/w) | overlap, metadata read | tcache poison / unsorted leak |
| double-free | dup → overlap | fastbin A-B-A / tcache-key bypass |
| heap overflow | metadata corruption | size-forge → consolidate overlap |
| off-by-one/NUL | size LSB corruption | overlap via P-bit clear |
| OOB index | bounded metadata write | fake chunk / fd poison |
| uninit chunk | leak | read stale fd/bk/data |
| double-alloc | shared memory | overlap → type confusion |

## The rule

The bug gives the primitive; the VERSION picks the technique. Never
pick a technique before both are named.
