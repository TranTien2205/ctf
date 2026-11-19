# tools/pwn_triage.py — the protection report — checklist

First contact: protections with the evidence for each, dangerous imports annotated, essential gadgets, and the routes each protection leaves open.

## Checklist

- [ ] python3 tools/pwn_triage.py ./chal — read the whole report.
- [ ] The report names each protection AND the evidence that decided it (not a guess).
- [ ] --gadgets lists every matched gadget, not just the essentials.
- [ ] --challenge <name> prints the command to record this triage in the challenge ledger.

## Abort conditions

- Absent-tool story: no pwntools/gdb/ROPgadget — this is the stdlib-only triage.
- A STATIC binary's __stack_chk_fail import doesn't mean the canary is enabled — read the evidence.
- python3 tools/pwnstatic/selftest.py proves the triage against readelf offline.

## Falsifier

Falsifier — the report and the binary disagree: the report's evidence is authoritative; re-read it.
