# Crash triage — what the fault says — checklist

Companion to `the-crash-triage.md`.

## Checklist

- [ ] Crash site | Meaning
- [ ] rip = 0x4141.. | the offset is wrong — re-measure
- [ ] rip = a gadget addr | landing right; the next stage's fault
- [ ] inside a called func on movaps | alignment — add a ret
- [ ] at a gadget's mid-instruction | wrong gadget address
- [ ] after the call, garbage | the ending isn't defined — add one
