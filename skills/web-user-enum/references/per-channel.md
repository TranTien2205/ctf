# Per-channel — each oracle channel's full protocol

| Channel | File | Probe | Delta | Falsifier |
|---|---|---|---|---|
| body text | `channel-body.md` | noise-masked `diff` | a byte/word/code difference | bad1==bad2 masked, good==bad |
| status+redirect | `channel-status.md` | `-w '%{http_code} %{redirect_url}'` | a code or `Location` difference | identical code+Location |
| timing | `channel-side.md`,`timing-oracle.md` | interleaved `time_total` | median delta >3x jitter | sub-jitter delta, N>=8 |
| side-artifact | `channel-side.md` | `-sv` envelope diff | a cookie/header/JSON-field difference | identical envelope |

## The channel-order rule

Cheapest first: body → status → side → timing. Body/status/side are
single-shot diffs; timing needs N≥8 samples. Try the cheap channels on
every form before paying for a timing baseline.

## The channel-coverage rule

A form is closed only when ALL FOUR are measured uniform — a uniform
body does not close a timing oracle; a uniform timing does not close a
`Set-Cookie` leak. Coverage, not "the first uniform channel".

## The channel-strength note

- body/status: the strongest, most reliable — a verbatim text/code delta
- side: strong when present, subtle — a cookie/field is unambiguous
- timing: the noisiest — real but jitter-swamped on weak hashes / remote
  targets; a median-of-many, never a single shot
