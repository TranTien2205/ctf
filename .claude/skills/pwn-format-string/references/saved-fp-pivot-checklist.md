# Saved-FP overwrite via %n — frame pivot — checklist

Companion to `saved-fp-pivot.md`.

## Checklist

- [ ] Observation | Meaning | Route
- [ ] saved RBP's stack addr known | pivot target | %n to it
- [ ] a controlled buffer elsewhere | pivot destination | the staged chain
- [ ] 1. Leak the saved RBP's stack address.
- [ ] 2. Write your staged-buffer address into saved RBP via %n.
- [ ] 3. On 'leave; ret': RSP=RBP (your buffer), then ret pops its first qword.
- [ ] 4. Your staged buffer holds the ROP chain.
- [ ] fomit-frame-pointer build (no saved RBP) or no known-address writable
