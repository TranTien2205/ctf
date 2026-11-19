# Detection checklist — is this the right route

## Run this class when

- [ ] the app is a SPA / ships a JS bundle (React, Vue, Next, Angular)
- [ ] the entry page loads `<script src>` bundles, not just CDN libs
- [ ] the front-end is the only source (white-box absent)
- [ ] a `//# sourceMappingURL=` or `.map` reference exists
- [ ] the rendered page hides routes the bundle might name

## The build fingerprint

- [ ] identified the bundler (webpack/Vite/Rollup/esbuild) and framework
- [ ] enumerated every chunk the page loads
- [ ] for Next.js, fetched `_buildManifest.js` for the route list
- [ ] probed `.map` siblings for every bundle

## The mining pass

- [ ] `bundle_miner --url` (or `--file`/`--map`) run and output read
- [ ] recovered `sourcesContent` read where it exists
- [ ] endpoint strings extracted from every bundle
- [ ] secret candidates checked with `--show-secrets`
- [ ] config/env/feature-flag strings grepped

## The verification

- [ ] each endpoint probed live — real response or 404?
- [ ] each secret verified — authenticates or dead?
- [ ] each flag traced to its gated endpoint
- [ ] a flag-shaped string gated through `pre-flag`

## The route decision

- [ ] leads routed to their classes
- [ ] dead leads recorded as negatives
- [ ] a clean "nothing actionable" recorded if the route is dead
