# Recon order — the first commands — checklist

Companion to `recon-order.md`.

## Checklist

- [ ] 1. `file ./chal` — architecture.
- [ ] 2. `python3 tools/pwn_triage.py ./chal` — protections (RELRO decides GOT).
- [ ] 3. `r2 -A ./chal && afl` — functions.
- [ ] 4. `r2 -A ./chal && pdf @ <func>` — find the printf call.
- [ ] 5. Check the format position: is your input the format or an argument?
- [ ] 6. Send %p.%p.%p — confirm the leak.
- [ ] 7. AAAA.%N$p sweep — the argument offset.
- [ ] 8. Choose read or write by the chain's need.
