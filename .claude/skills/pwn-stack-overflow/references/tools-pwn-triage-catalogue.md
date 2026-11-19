# tools/pwn_triage.py — the protection report — case catalogue

First contact: protections with the evidence for each, dangerous imports annotated, essential gadgets, and the routes each protection leaves open.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | --gadgets for the full list | gadget inventory | finds pops/rets/syscall |
| 2 | --challenge <name> prints the ledger command | record the triage | state.json integration |
| 3 | essential gadget set | pop rdi/rsi/rdx + syscall + ret | the minimum chain |

## Falsifier

Falsifier — the report and the binary disagree: the report's evidence is authoritative; re-read it.
