# web-csrf references — the index

Depth files for cross-site request forgery. Open ONE file based on
the gate you're measuring — never read them all.

## Start here

| File | When to open |
|---|---|
| `workflow.md` | the end-to-end procedure — inventory, gates, delivery, readback |
| `field-manual.md` | the operational checklist — commands in order |
| `cheatsheet.md` | the one-page reference — gates, carriers, payloads |
| `verified-chains.md` | the two grounded card shapes — TornadoService + SSOS |
| `detection-checklist.md` | the rapid 90-second screen |
| `exploitation-playbook.md` | the 15 named plays |
| `real-world-patterns.md` | the recurring challenge shapes |
| `frameworks-deep.md` | per-stack CSRF internals |
| `glossary.md` | the class's terms |

## The gate-measurement layer

| File | The gate it covers |
|---|---|
| `detection.md` | the class signals and first reads |
| `detection-deep.md` | the signal→skill routing and black-box signals |
| `endpoint-inventory.md` | finding the state-changing surface |
| `samesite-matrix.md` | when the browser attaches the cookie |
| `cookie-attributes-deep.md` | beyond SameSite — Secure/HttpOnly/Path/Domain/Partitioned |
| `token-defenses.md` | every CSRF-token shape and its failure modes |
| `token-bypass-deep.md` | the verification-logic failure corpus |
| `origin-referer.md` | the header checks and their gaps |
| `headers-deep.md` | the full request-header surface — Sec-Fetch, safelisted, spoofable |
| `content-type-gate.md` | which content-type a form can send |

## The delivery layer

| File | The carrier it covers |
|---|---|
| `delivery-shapes.md` | every auto-firing form/fetch/img/nav shape |
| `delivery-vectors.md` | the carrier→SameSite→content-type matrix |
| `json-body-assembly.md` | the text/plain JSON trick — the `=` absorption |
| `payload-dictionary.md` | ~250 categorized payloads |
| `extended-corpus.md` | the deep payload/case library |
| `multi-step-and-race.md` | chained writes and the timing shapes |
| `method-override.md` | reaching PUT/DELETE writes through a POST form |
| `content-type-carriers.md` | the deep parse-shape corpus per content-type |
| `delivery-edge-cases.md` | the corner carriers and their traps |
| `delivery-contexts.md` | where the CSRF page can live — external/data:/stored/subdomain |
| `subresource-and-nav.md` | the top-nav vs sub-resource SameSite decision |
| `browser-behavior-matrix.md` | the engine/version differences that decide CSRF |
| `internal-networks.md` | writes the bot reaches that you can't |
| `payload-variants.md` | the complete form/body library by write-type |
| `write-types-index.md` | the endpoint → payload → oracle lookup |
| `evasion-and-waf.md` | when a filter inspects the delivery |

## The viewer layer

| File | The delivery vehicle |
|---|---|
| `bot-triage.md` | characterizing the bot — credentials, reach, lifecycle |
| `bot-delivery.md` | the bot-does-the-write patterns |
| `pna-and-loopback.md` | Private Network Access + the loopback-write gate |
| `websocket-csrf.md` | the ws/wss channel opened cross-origin |
| `privilege-boundary.md` | writes that need the admin's session |

## The write-semantics layer

| File | The write it covers |
|---|---|
| `login-csrf.md` | the credential-plant write — the SSOS shape |
| `oauth-sso-csrf.md` | the OAuth/SSO flow-level CSRF |
| `stored-and-second-order.md` | the same-origin stored-CSRF bypass |
| `same-origin-vectors.md` | the CSRF that isn't cross-site — stored/subdomain/same-site |
| `csrf-chains.md` | what the write unlocks — XSS, takeover, escalation |
| `write-semantics.md` | what each endpoint type's CSRF actually does |
| `form-fields-corpus.md` | the write's parameter/field dictionary |
| `case-studies.md` | worked end-to-end walkthroughs |
| `cors-interplay.md` | the CSRF↔CORS read/write boundary |

## The discipline layer

| File | The rule it covers |
|---|---|
| `readback-oracles.md` | proving a blind CSRF landed |
| `evidence-rules.md` | the confirms/refutes/flag bar |
| `negative-results.md` | recording the gates that held |
| `troubleshoot.md` | when the delivery fails — symptom→gate |
| `delivery-troubleshoot.md` | the firing-side failures — page/bot/carrier |
| `common-mistakes.md` | the failure modes to avoid |
| `class-boundary.md` | CSRF vs XSS/CORS/SSRF/XS-leaks |
| `theory.md` | the ambient-authority model |
| `summary.md` | the mental model in one page |
| `audit-checklist.md` | the pre-flight and post-landing checks |
| `common-questions.md` | the CSRF FAQ |
