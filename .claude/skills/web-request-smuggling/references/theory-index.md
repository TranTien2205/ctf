# Theory index — the parsing model's map

## The byte-stream — the request is text

`theory-primitives.md` — the request is bytes, boundaries are computed.

## The two parsers — the front and the back

`smuggle-mechanism.md` — the front parses, re-emits, the back parses.

## The boundary-signals — three ways to find the body's end

`theory-primitives.md` — `Content-Length` / `Transfer-Encoding` / `close`.

## The precedence — TE wins over CL

`theory-primitives.md` — RFC 7230 §3.3.3 — but "TE" means `chunked` is
recognized — `obfuscation.md`.

## The parser-states — the byte-machine

`desync-mechanism.md` — request-line → headers → body → next-request.

## The pair-taxonomy — the disagreements

`desync-taxonomy.md` — CL.TE / TE.CL / TE.TE / CL.CL / CL.0 / H2.*.

## The keep-alive — the next-request exists

`queue-management.md` — `Connection: keep-alive`.

## The trust — the back trusts the front's output

`frontend-bypass.md`.

## The upgrade — the parser-exit

`tunneling.md` / `upgrade-smuggling.md`.

## The downgrade — h2 → h1

`theory-downgrade.md` / `theory-downgrade-deep.md`.

## The smuggle — the bytes between boundaries

`smuggle-landing.md`.

## The readback — the smuggle's output

`smuggle-readback.md` / `desync-readback.md` / `desync-readback-deep.md`.

## The impact — the ladder

`desync-ladder.md`.

## The detection — the oracles

`detection.md` / `detection-oracle.md` / `desync-detection.md` /
`smuggle-detection-matrix.md`.

## The payloads — the byte-sequences

`payload-dictionary.md` / `smuggle-payloads.md` / `detection-payloads.md` /
`desync-corpus.md` / `ambiguity-catalog.md`.

## The exploitation — after the desync

`smuggle-exploitation.md` / `exploit-templates.md`.

## The bypass — the WAF/filter evasions

`smuggle-bypass.md`.

## The stability — the reliability

`smuggle-stability.md`.

## The traps — the failure modes

`smuggle-traps.md` / `common-mistakes.md`.

## The evidence — the verbatim excerpts

`evidence-rules.md` / `smuggle-evidence.md`.

## The denied — the no-smuggle conditions

`denied-conditions.md`.

## The cases — the challenge-level shapes

`smuggle-cases.md` / `ctf-shapes.md` / `real-world-cases.md`.

## The env — the proxy-pairs

`smuggle-env.md` / `proxy-behavior.md` / `container-world.md`.

## The workflow — the operator's sequence

`workflow.md` / `desync-workflow.md` / `smuggle-workflow.md` /
`desync-checklist.md` / `probe-sequences.md` / `field-manual.md` /
`cheatsheet.md`.

## The writeup — the chain's narrative

`smuggle-writeup.md`.

## The flags — the flag-locations

`flag-locations.md` / `desync-flags.md`.

## The internal — the routes and APIs

`internal-routes.md` / `internal-api.md` / `virtual-host.md` /
`header-smuggling.md` / `advanced-headers.md`.

## The protocol — the crossings and versions

`protocol-crossing.md` / `protocol-version.md` / `http10-desync.md` /
`content-type-boundary.md` / `method-boundary.md` / `http-pipelining.md`.

## The headers — the boundary-headers

`header-boundary.md` / `header-smuggling.md` / `advanced-headers.md`.

## The attack-defense — the AD plane

`attack-defense.md`.

## The tooling — the repo's primitives

`tooling.md`.

## The white-box — the source-hunt

`whitebox-hunt.md`.

## The second-order — the deferred

`second-order.md` / `webhook-deferred.md` / `blind-smuggle.md` /
`blind-desync.md`.

## The error — the error-analysis

`error-analysis.md`.
