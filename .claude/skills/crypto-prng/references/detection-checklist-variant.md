# Detection checklist variant — the gate list, terse

## The reads

- [ ] generator named/fingerprinted — or `urandom` → out.
- [ ] outputs consecutive + raw.
- [ ] shape noted — int/hex/float/bit/`mod`/`>>`.
- [ ] seed/`iat`/params visible.

## The gates

- [ ] count ≥ floor — 3/6/req/2w/624/4.
- [ ] outputs normalized — ints.
- [ ] aligned — no gaps/reseed.
- [ ] params known — `m`/`a,c`/taps/`low-bits`/window.

## The route

- [ ] family — lcg/lfsr/mt/xorshift/seed.
- [ ] attack — the param-known column.
- [ ] command — real flags.

## The close

- [ ] `predict==held` plan.
- [ ] flag shape expected.
- [ ] `post-probe`/`pre-flag` ready.
