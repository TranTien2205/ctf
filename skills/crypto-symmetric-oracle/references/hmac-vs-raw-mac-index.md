# HMAC vs raw-hash MAC — the extension boundary — index

Length extension exists because sha1(secret||m) leaks its chaining state. HMAC wraps the key into two pads and closes that channel. Telling them apart is a one-probe question.

## Related modules

- `hmac-vs-raw-mac-deep.md` — mechanism internals and boundary conditions
- `hmac-vs-raw-mac-checklist.md` — the ordered operational steps
- `hmac-vs-raw-mac-catalogue.md` — case enumeration

## Cross-references

`length-extension.md` · `mac-forgery.md`
