# Workflow — the ordered path from binary to flag

## Phase 1 — triage (tools, once)

```bash
python3 tools/pwn_triage.py ./chal           # protections + evidence
python3 tools/pwn_triage.py ./chal --gadgets # full gadget list
r2 -A ./chal && afl                          # function inventory
```

The protections sheet decides the chain before any payload is written.

## Phase 2 — the sink

White-box: grep the dangerous set (`gets`, `strcpy`, `scanf %s`,
`read(fd,buf,n)` with influenced n, `sprintf`). Black-box: growing-length
inputs until the crash appears.

## Phase 3 — the offset

`python3 tools/pwn_cyclic.py <N>` → send → fault → `--find <4 bytes>`.
The offset is measured, never guessed.

## Phase 4 — the chain (by protections)

| Protections | Chain |
|---|---|
| NX off | `ret2shellcode.md` + `tools-sc-gen.md` |
| NX on, func in binary | `ret2win.md` |
| NX on, system imported | `ret2plt.md` |
| NX on, libc linked + leak | `ret2libc.md` |
| Canary + leak | `canary-bypass.md` |
| PIE | `pie-leak.md` first |
| partial RELRO + write | `fgot-overwrite.md` |
| sparse gadgets | `ret2csu.md` / `srop.md` |

## Phase 5 — evidence

The crash-dump register state is the offset evidence; the flag in the
response is the impact. post-probe for the class claim, pre-flag for the
bytes.
