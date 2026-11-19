# Mechanism index — every component of the redirect mechanism, mapped

## The component index

| The component | The file | The summary |
|---|---|---|
| the param | `param-inventory.md`, `per-param.md` | the 100-name vocabulary + the context |
| the filter | `filter-bypass-deep.md`, `per-check.md` | the check-shapes + the defeating arms |
| the resolution | `mechanism-deep.md` | how the param becomes the Location |
| the carrier | `detection.md`, `client-side.md`, `stored-and-referer.md` | the Location/meta/JS/Refresh |
| the navigation | `parser-differentials.md` | the WHATWG parse the browser does |
| the launder | `chain-routes.md`, `per-route.md` | the downstream trust |
| the fingerprint | `decision-table.md`, `detection-matrix.md` | the Location-shape → the arms |
| the falsifier | `falsifiers.md`, `falsifiers-deep.md` | the class-closing observations |

## The mechanism-to-arm map — the complete index

```text
the param surface
  -> per-param.md          the param-name contexts
  -> param-inventory.md    the full vocabulary
  -> per-endpoint.md       the endpoint × param matrix
  -> per-surface.md        the surface × param matrix

the filter surface
  -> filter-bypass-deep.md the check-shape × arm matrix
  -> per-check.md          the per-check arms
  -> parser-differentials.md the two-parser gaps
  -> framework-matrix.md   the framework-check × arm
  -> encoding-attacks.md   the decode-order arms
  -> evasion.md            the residual arms

the carrier surface
  -> detection.md          the Location/Refresh/meta/JS detection
  -> client-side.md        the meta/JS/hash twins
  -> stored-and-referer.md the stored/Referer surfaces
  -> edge-cases.md         the unusual carriers

the navigation surface
  -> parser-differentials.md the WHATWG-vs-filter parse
  -> mechanism-deep.md     the full component model

the launder surface
  -> chain-routes.md       the OAuth/SSRF/XSS/bot/phishing routes
  -> per-route.md          the per-route reachability
  -> multi-step-chains.md  the two/three-hop chains
  -> attack-shapes.md      the canonical exploits
  -> exploitation.md       the confirm-to-flag procedure
```

## The verdict index — where each verdict lives

```text
the candidate/confirm  -> evidence-rules.md / evidence-rules-deep.md
the falsifier          -> falsifiers.md / falsifiers-deep.md
the negative           -> negative-results.md / negative-results-deep.md
the troubleshoot       -> troubleshoot.md
the edge               -> edge-cases.md
the mistake            -> common-mistakes.md
the question           -> common-questions.md
```

## The mechanism-record

`mechanism-index: <the-component> -> <the-file>` — the component's deep file.
