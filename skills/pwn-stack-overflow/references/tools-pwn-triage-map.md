# tools/pwn_triage.py — the protection report — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| --gadgets for the full list | gadget inventory | finds pops/rets/syscall |
| --challenge <name> prints the ledger command | record the triage | state.json integration |
| essential gadget set | pop rdi/rsi/rdx + syscall + ret | the minimum chain |

## Falsifier

Falsifier — the report and the binary disagree: the report's evidence is authoritative; re-read it.
