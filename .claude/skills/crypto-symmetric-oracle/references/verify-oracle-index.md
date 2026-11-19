# Verify oracle — tag checking as a distinguisher — index

A verify endpoint that answers 'tag good' vs 'tag bad' is an oracle on the authentication side. Timing in the compare function, truncation, and acceptance of malformed tags all leak.

## Related modules

- `verify-oracle-deep.md` — mechanism internals and boundary conditions
- `verify-oracle-checklist.md` — the ordered operational steps
- `verify-oracle-catalogue.md` — case enumeration

## Cross-references

`mac-forgery.md` · `response-distinguishers.md`
