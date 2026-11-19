# tools/pwn_triage.py — the protection report

First contact: protections with the evidence for each, dangerous imports annotated, essential gadgets, and the routes each protection leaves open.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --gadgets for the full list | gadget inventory | finds pops/rets/syscall |
| --challenge <name> prints the ledger command | record the triage | state.json integration |
| essential gadget set | pop rdi/rsi/rdx + syscall + ret | the minimum chain |

## Steps

1. python3 tools/pwn_triage.py ./chal — read the whole report.
2. The report names each protection AND the evidence that decided it (not a guess).
3. --gadgets lists every matched gadget, not just the essentials.
4. --challenge <name> prints the command to record this triage in the challenge ledger.

## Falsifier

Falsifier — the report and the binary disagree: the report's evidence is authoritative; re-read it.

## Traps

- Absent-tool story: no pwntools/gdb/ROPgadget — this is the stdlib-only triage.
- A STATIC binary's __stack_chk_fail import doesn't mean the canary is enabled — read the evidence.
- python3 tools/pwnstatic/selftest.py proves the triage against readelf offline.

## Commands

```bash
python3 tools/pwn_triage.py ./chal
python3 tools/pwn_triage.py ./chal --gadgets
python3 tools/pwnstatic/selftest.py
```

## Cross-references

`protection-modes.md`
