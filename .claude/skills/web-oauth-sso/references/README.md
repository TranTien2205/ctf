# OAuth/SSO reference map

This directory belongs to the canonical `web-oauth-sso` class skill.
Open the named file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| The full walk — commands, expected outputs, decision points | `field-manual.md` |
| The quick map — the falsifier sweep and the decision tree | `quick-reference.md` |
| The detection surface — artifact → mechanism → probe | `detection.md` |
| The detection matrix — the artifact index | `detection-matrix.md` |
| The detection checklist — the artifacts in order | `detection-checklist.md` |
| The detection index — the artifact index | `detection-index.md` |
| The detection deep — the full mechanics | `detection-deep.md` |
| The mechanism alphabet — mechanism → artifact → falsifier | `per-mechanism.md` |
| The mechanism index — mechanism → probe → falsifier | `per-mechanism-index.md` |
| The per-check index — check → probe → falsifier | `per-check-index.md` |
| The per-check falsifier — falsifier → reclassification | `per-check-falsifier.md` |
| The per-check CSRF — `state` binding | `per-check-csrf.md` |
| The per-check redirect — `redirect_uri` validation | `per-check-redirect.md` |
| The per-check cookie — `SameSite` validation | `per-check-cookie.md` |
| The per-check linking — account linking | `per-check-linking.md` |
| The per-check implicit — `response_type` allowlist | `per-check-implicit.md` |
| The per-check PKCE — `code_challenge` validation | `per-check-pkce.md` |
| The per-check scope — `scope` allowlist | `per-check-scope.md` |
| The per-check registration — registration idempotency | `per-check-registration.md` |
| The per-check token — `client_id` binding | `per-check-token.md` |
| The per-check client — `aud` verification | `per-check-client.md` |
| The per-check signature — `signature` verification | `per-check-signature.md` |
| The per-check nonce — `nonce` validation | `per-check-nonce.md` |
| The per-check response-mode — `response_mode` validation | `per-check-response-mode.md` |
| The per-check exchange — `token` exchange | `per-check-exchange.md` |
| The per-check binding — `code` binding | `per-check-binding.md` |
| The per-check delivery — `delivery` validation | `per-check-delivery.md` |
| The per-check flow — `flow` shape | `per-check-flow.md` |
| The per-surface — attack surface → probe → falsifier | `per-surface.md` |
| The per-route — route → probe → falsifier | `per-route.md` |
| The per-vector — attack vector → chain → sink | `per-vector.md` |
| The per-boundary — trust boundary → break → falsifier | `per-boundary.md` |
| The exploitation playbook — chain → sink | `exploitation-playbook.md` |
| The exploitation shapes — chain → sink | `exploitation-shapes.md` |
| The exploitation deep — the full mechanics | `exploitation.md` |
| The multi-step chains — chain → sink | `multi-step-chains.md` |
| The payload dictionary — request bodies | `payload-dictionary.md` |
| The payload dictionary deep — request bodies | `payload-dictionary-deep.md` |
| The theory — the trust model | `theory.md` |
| The theory deep — the trust model | `theory-deep.md` |
| The evidence rules — the verbatim excerpts | `evidence-rules.md` |
| The evidence rules deep — the verbatim excerpts | `evidence-rules-deep.md` |
| The falsifiers — the observations that close each shape | `falsifiers.md` |
| The falsifiers deep — the observations that close each shape | `falsifiers-deep.md` |
| The negative results — the observations that are not confirmations | `negative-results.md` |
| The negative results deep — the observations that are not confirmations | `negative-results-deep.md` |
| The edge cases — the surfaces that are easy to miss | `edge-cases.md` |
| The edge cases deep — the surfaces that are easy to miss | `edge-cases-deep.md` |
| The evasion — the surfaces that are easy to miss | `evasion.md` |
| The common mistakes — the mistakes that cost time | `common-mistakes.md` |
| The common mistakes deep — the mistakes that cost time | `common-mistakes-deep.md` |
| The common questions — the decisions | `common-questions.md` |
| The common questions deep — the decisions | `common-questions-deep.md` |
| The troubleshoot — when the probes fail | `troubleshoot.md` |
| The troubleshoot deep — when the probes fail | `troubleshoot-deep.md` |
| The framework matrix — the implementations by stack | `framework-matrix.md` |
| The class boundary — where web-oauth-sso ends | `class-boundary.md` |
| The class boundary deep — where web-oauth-sso ends | `class-boundary-deep.md` |
| The verified chains — the chain cards | `verified-chains.md` |
| The case studies — the shapes that have been solved | `case-studies.md` |
| The case studies deep — the shapes that have been solved | `case-studies-deep.md` |
| The real-world cases — the shapes that have been solved | `real-world-cases.md` |
| The extended corpus — the shapes that are not on the checklist | `extended-corpus.md` |
| The workflow — the audit sequence | `workflow.md` |
| The workflow deep — the audit sequence | `workflow-deep.md` |
| The workflow checklist — the audit sequence | `workflow-checklist.md` |
| The checklist — the audit in order | `checklist.md` |
| The summary — the skill at a glance | `summary.md` |
| The glossary — the vocabulary | `glossary.md` |
| The whitebox hunt — the source-level signals | `whitebox-hunt.md` |
| The flow abuse — the flow shape | `flow-abuse.md` |
| The authorization-code flow — the flow shape | `authorization-code-flow.md` |
| The redirect URI — the delivery target | `redirect-uri.md` |
| The SAML — the SAML shape | `saml.md` |
| The account linking — the linking model | `account-linking.md` |
| The cookie swap — the cookie model | `cookie-swap.md` |
| The state parameter — the CSRF binding | `state-parameter.md` |
| The token binding — the token model | `token-binding.md` |
| The client confusion — the client model | `client-confusion.md` |
| The implicit flow — the implicit shape | `implicit-flow.md` |
| The PKCE — the PKCE shape | `pkce.md` |
| The scope — the permission model | `scope.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a reference file only when the signal or task names it.
