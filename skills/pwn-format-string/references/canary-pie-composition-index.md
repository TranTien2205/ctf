# Canary + PIE leak composition — defeating both at once — index

PIE and a canary together need TWO leaks: a code pointer for the base AND the canary word. The fmtstr's %p run can leak both in one call.

## Related modules

- `canary-pie-composition-deep.md` — boundary conditions
- `canary-pie-composition-checklist.md` — operational steps
- `canary-pie-composition-catalogue.md` — case enumeration

## Cross-references

`leak-via-p.md` · `skip-canary-by-write.md`
