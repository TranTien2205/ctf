# Length extension — hash(secret||msg) forgery — index

A MAC built as sha1/sha256/md5 of secret||message is forgeable: the hash's internal state after the message is the digest itself — continue it with your appended data.

## Related modules

- `length-extension-deep.md` — mechanism internals and boundary conditions
- `length-extension-variant.md` — when the surface shape changes
- `length-extension-checklist.md` — the ordered operational steps
- `length-extension-catalogue.md` — case enumeration

## Cross-references

`tools-length-extension.md` · `mac-forgery.md` · `hmac-vs-raw-mac.md`
