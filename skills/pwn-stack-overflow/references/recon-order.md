# Recon order — the first eight commands

The cheapest signals first, the expensive last.

1. `python3 tools/pwn_triage.py ./chal` — the protections report.
2. `python3 tools/pwn_triage.py ./chal --gadgets` — the gadget inventory.
3. `file ./chal` — architecture, static/dynamic, stripped.
4. `readelf -h ./chal | grep Type` — PIE check.
5. `readelf -s ./chal | grep FUNC` — the import inventory.
6. `strings -tx ./chal | grep -iE 'sh$|flag'` — candidate strings.
7. `r2 -A ./chal && afl` — function list.
8. `r2 -A ./chal && pdf @ <vuln>` — the deciding disassembly.

The triage report is the first deliverable; it names the protections AND
the evidence for each. Everything downstream routes from it.
