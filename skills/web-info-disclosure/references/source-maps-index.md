# Source maps — .map files and the front-end's real source — index

A deployed .map file reverses the minification: sourcesContent contains the original code, including endpoints, feature flags, and sometimes secrets. tools/web/bundle_miner.py automates recovery.

## Related modules

- `source-maps-deep.md` — mechanism internals and boundary conditions
- `source-maps-checklist.md` — the ordered operational steps
- `source-maps-catalogue.md` — case enumeration

## Cross-references

`tools-bundle-miner.md` · `../web-source-map/` · `secrets-in-js.md`
