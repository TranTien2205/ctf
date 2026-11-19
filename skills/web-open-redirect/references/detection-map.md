# Detection map — the signal-to-file navigation

## The "I see X" map

| You observed | Open |
|---|---|
| a `?next=`/`?url=`/`?redirect=` param | `param-inventory.md`, `per-param.md` |
| a 302 with a `Location:` | `detection.md`, `evidence-rules.md` |
| a `Location:` carrying your canary | `evidence-rules-deep.md` → post-probe |
| a `Location: /`/`Location: <safe>` | `falsifiers.md`, `decision-table.md` |
| a `Location:` you can't read the host of | `parser-differentials.md` |
| a meta-refresh | `client-side.md` |
| a `location.href`/`location=` | `client-side.md` |
| a `location.hash` | `client-side.md` |
| a Referer-driven 302 | `stored-and-referer.md` |
| a `Refresh:` header | `client-side.md`, `edge-cases.md` |
| a param in a bundle's `location.*` | `client-side.md`, `per-surface.md` |
| a param that persists | `stored-and-referer.md` |
| a 302 on an OAuth flow | `chain-routes.md`, `per-endpoint.md` |
| a fetcher that follows a redirect | `chain-routes.md`, `per-route.md` |
| a `Location:` that doesn't cross origin | `edge-cases.md` (`Location: evil.com` relative) |
| a `Location: <partial>` | `decision-table.md`, `detection-matrix.md` |
| every arm -> `Location: <safe>` | `falsifiers-deep.md` |
| a `400`/`422` on the canary | `troubleshoot.md` |
| no `Location` at all | `troubleshoot.md`, `negative-results.md` |

## The "I want to do X" map

| Your task | Open |
|---|---|
| find the redirect params | `param-inventory.md`, `per-endpoint.md` |
| run the first canary | `quick-reference.md`, `field-manual.md` |
| read the fingerprint | `decision-table.md`, `detection-matrix.md` |
| pick a bypass arm | `filter-bypass-deep.md`, `per-check.md`, `per-vector.md` |
| run the arms | `payload-dictionary.md`, `payload-variants.md` |
| check the client-side | `client-side.md` |
| check the stored/Referer | `stored-and-referer.md` |
| route to a chain | `chain-routes.md`, `per-route.md`, `multi-step-chains.md` |
| record the verdict | `evidence-rules-deep.md` |
| close the class | `falsifiers-deep.md`, `negative-results-deep.md` |
| the framework's check | `framework-matrix.md` |
| a case like this one | `case-studies.md`, `real-world-cases.md` |
| the edge/trap | `edge-cases.md`, `common-mistakes.md` |

## The reference-tree map

```text
references/
  mechanism*.md          the model
  detection*.md          the signals
  filter-bypass*.md      the bypass corpus
  parser-differentials.md the parse gaps
  framework-matrix.md    the per-framework checks
  encoding-attacks.md    the decode-order
  payload-*.md           the arms
  per-*.md               the per-axis maps
  client-side.md         the meta/JS/hash twins
  stored-and-referer.md  the two-step + header surfaces
  chain-*.md             the laundered-trust routes
  evidence-*.md          the verbatim-Location standard
  falsifier*.md          the class-closing
  negative-*.md          the negative taxonomy
  workflow*.md           the ordered procedure
  field-manual.md        the operating procedure
  troubleshoot.md        the when-it-fails
  edge-cases.md          the unusual
  common-*.md            the mistakes + questions
  evasion.md             the residual arms
  case-studies.md        the named shapes
  theory.md              the why
  glossary.md            the terms
  class-boundary.md      the sibling-class boundary
  checklist.md           the verification pass
  onboarding.md          the first 15 minutes
  decision-table.md      the fingerprint -> arm -> verdict
  mechanism-index.md     the component -> file map
  detection-index.md     the signal -> file map
  detection-catalogue.md the signal catalogue
  detection-map.md       the navigation map
  verified-chains.md     the honest local state
```
