# Response anatomy — what each status really means — operational checklist

A bounded sweep is only as good as its read of each response. 200 is not 'found' and 403 is not 'absent' — content decides.

## Checklist

- [ ] Baseline the catch-all: request a known-bogus path, save the response.
- [ ] Diff each probe's response against the baseline — same body = no hit.
- [ ] A 403 on a real path: try other verbs, Host/Forwarded headers, trailing slash.
- [ ] Content-length + body hash are the discriminator when statuses lie.

## Abort conditions

- Catch-alls often return 200 for everything — status is meaningless alone.
- A 403 that flips to 200 with a different Host header is a real finding.
- Content-length alone lies on templated pages — hash the body.

## Falsifier

Falsifier — every probed path returns the identical catch-all body: nothing in the bounded list is exposed. Wider fuzzing is out of scope for this class.

## Cross-references

`detection-matrix.md` · `catchall-falsifier.md`
