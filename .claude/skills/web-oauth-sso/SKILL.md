---
name: web-oauth-sso
description: >
  Action-oriented depth skill for OAuth / SSO flow. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-auth-session, web-open-redirect.
  Verified here by 1 chain card(s).
tags: [web, oauth-sso, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: verified
---
# OAuth / SSO flow

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-ssos-oauth-registration-race-cookie-swap-json-csrf.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

walk the whole flow once and record every redirect, parameter and cookie set, before changing any of them

**Falsifier** — the observation that closes this class: the state parameter is bound to the session and the redirect target is a strict allowlist
## Recognise

An authorisation flow across two parties: an identity provider and the
application, joined by redirects, a code and a state parameter. Multiple session
cookies usually appear — one per party. A `SAMLResponse`/`SAMLRequest`
parameter in that transcript is the SAML shape:
`python3 tools/web/saml_decode.py resp.txt` decodes the base64
(optionally DEFLATE'd) XML and lists Issuer, NameID, attributes and
whether the assertion is signed — signature-removal, comment-injection
and attribute-edit tests start from that inventory.

## Confirm

**Walk the whole flow once and record everything before changing anything**: every
redirect, every parameter, every cookie set and by whom. Most findings in this
class are visible in that transcript, and a change made before the transcript
exists is unattributable.

## What goes wrong

| Where | Shape |
|---|---|
| State parameter | not bound to the session, so a flow can be started by one party and finished by another |
| Redirect target | validated loosely, so the code is delivered somewhere it should not be |
| Account linking | identity matched on an address the attacker can also register |
| Two cookies | the application and the provider each set one, and swapping them at the right moment crosses the identities |

The last one is why the transcript matters: the exploit lives in the ordering of
cookie writes, not in any single request.

## Traps

- A registration step inside the flow can be raced; see `../web-race-condition/`.
- Changing a redirect target usually invalidates the code. Test the validation
  first with a harmless variation.

## Operational probe

```bash
curl -i -b "$JAR" -L "$BASE/oauth/callback?code=AAAA&state=BBBB"
```

Replay the callback with a `state` the provider never issued for this session,
then with the code swapped for another user's (if a second account exists).
Record the verbatim status line and any session issued. Confirmation: a
session or token issued against a mismatched state or a foreign code. A 400
naming the mismatch closes the path — record it as the falsifier.

## Routing

Shares signals with: `../web-auth-session/`, `../web-open-redirect/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/web-auth-session/references/oauth-flow-issues.md`
- `skills/ctf-web/auth-infra.md`

| Signal or task | Open |
|---|---|
| The full walk — commands, expected outputs, decision points | `references/field-manual.md` |
| The quick map — the falsifier sweep and the decision tree | `references/quick-reference.md` |
| The detection surface — artifact → mechanism → probe | `references/detection.md` |
| The detection matrix — the artifact index | `references/detection-matrix.md` |
| The detection checklist — the artifacts in order | `references/detection-checklist.md` |
| The detection index — the artifact index | `references/detection-index.md` |
| The detection deep — the full mechanics | `references/detection-deep.md` |
| The mechanism alphabet — mechanism → artifact → falsifier | `references/per-mechanism.md` |
| The mechanism index — mechanism → probe → falsifier | `references/per-mechanism-index.md` |
| The per-check index — check → probe → falsifier | `references/per-check-index.md` |
| The per-check falsifier — falsifier → reclassification | `references/per-check-falsifier.md` |
| The per-check CSRF — `state` binding | `references/per-check-csrf.md` |
| The per-check redirect — `redirect_uri` validation | `references/per-check-redirect.md` |
| The per-check cookie — `SameSite` validation | `references/per-check-cookie.md` |
| The per-check linking — account linking | `references/per-check-linking.md` |
| The per-check implicit — `response_type` allowlist | `references/per-check-implicit.md` |
| The per-check PKCE — `code_challenge` validation | `references/per-check-pkce.md` |
| The per-check scope — `scope` allowlist | `references/per-check-scope.md` |
| The per-check registration — registration idempotency | `references/per-check-registration.md` |
| The per-check token — `client_id` binding | `references/per-check-token.md` |
| The per-check client — `aud` verification | `references/per-check-client.md` |
| The per-check signature — `signature` verification | `references/per-check-signature.md` |
| The per-check nonce — `nonce` validation | `references/per-check-nonce.md` |
| The per-check response-mode — `response_mode` validation | `references/per-check-response-mode.md` |
| The per-check exchange — `token` exchange | `references/per-check-exchange.md` |
| The per-check binding — `code` binding | `references/per-check-binding.md` |
| The per-check delivery — `delivery` validation | `references/per-check-delivery.md` |
| The per-check flow — `flow` shape | `references/per-check-flow.md` |
| The per-check SSO — `loginSSO` check | `references/per-check-sso.md` |
| The per-surface — attack surface → probe → falsifier | `references/per-surface.md` |
| The per-route — route → probe → falsifier | `references/per-route.md` |
| The per-vector — attack vector → chain → sink | `references/per-vector.md` |
| The per-boundary — trust boundary → break → falsifier | `references/per-boundary.md` |
| The exploitation playbook — chain → sink | `references/exploitation-playbook.md` |
| The exploitation shapes — chain → sink | `references/exploitation-shapes.md` |
| The exploitation deep — the full mechanics | `references/exploitation.md` |
| The multi-step chains — chain → sink | `references/multi-step-chains.md` |
| The payload dictionary — request bodies | `references/payload-dictionary.md` |
| The payload dictionary deep — request bodies | `references/payload-dictionary-deep.md` |
| The theory — the trust model | `references/theory.md` |
| The theory deep — the trust model | `references/theory-deep.md` |
| The evidence rules — the verbatim excerpts | `references/evidence-rules.md` |
| The evidence rules deep — the verbatim excerpts | `references/evidence-rules-deep.md` |
| The falsifiers — the observations that close each shape | `references/falsifiers.md` |
| The falsifiers deep — the observations that close each shape | `references/falsifiers-deep.md` |
| The negative results — the observations that are not confirmations | `references/negative-results.md` |
| The negative results deep — the observations that are not confirmations | `references/negative-results-deep.md` |
| The edge cases — the surfaces that are easy to miss | `references/edge-cases.md` |
| The edge cases deep — the surfaces that are easy to miss | `references/edge-cases-deep.md` |
| The evasion — the surfaces that are easy to miss | `references/evasion.md` |
| The common mistakes — the mistakes that cost time | `references/common-mistakes.md` |
| The common mistakes deep — the mistakes that cost time | `references/common-mistakes-deep.md` |
| The common questions — the decisions | `references/common-questions.md` |
| The common questions deep — the decisions | `references/common-questions-deep.md` |
| The troubleshoot — when the probes fail | `references/troubleshoot.md` |
| The troubleshoot deep — when the probes fail | `references/troubleshoot-deep.md` |
| The framework matrix — the implementations by stack | `references/framework-matrix.md` |
| The class boundary — where web-oauth-sso ends | `references/class-boundary.md` |
| The class boundary deep — where web-oauth-sso ends | `references/class-boundary-deep.md` |
| The verified chains — the chain cards | `references/verified-chains.md` |
| The case studies — the shapes that have been solved | `references/case-studies.md` |
| The case studies deep — the shapes that have been solved | `references/case-studies-deep.md` |
| The real-world cases — the shapes that have been solved | `references/real-world-cases.md` |
| The extended corpus — the shapes that are not on the checklist | `references/extended-corpus.md` |
| The workflow — the audit sequence | `references/workflow.md` |
| The workflow deep — the audit sequence | `references/workflow-deep.md` |
| The workflow checklist — the audit sequence | `references/workflow-checklist.md` |
| The checklist — the audit in order | `references/checklist.md` |
| The summary — the skill at a glance | `references/summary.md` |
| The glossary — the vocabulary | `references/glossary.md` |
| The whitebox hunt — the source-level signals | `references/whitebox-hunt.md` |
| The flow abuse — the flow shape | `references/flow-abuse.md` |
| The authorization-code flow — the flow shape | `references/authorization-code-flow.md` |
| The redirect URI — the delivery target | `references/redirect-uri.md` |
| The SAML — the SAML shape | `references/saml.md` |
| The account linking — the linking model | `references/account-linking.md` |
| The cookie swap — the cookie model | `references/cookie-swap.md` |
| The state parameter — the CSRF binding | `references/state-parameter.md` |
| The token binding — the token model | `references/token-binding.md` |
| The client confusion — the client model | `references/client-confusion.md` |
| The implicit flow — the implicit shape | `references/implicit-flow.md` |
| The PKCE — the PKCE shape | `references/pkce.md` |
| The scope — the permission model | `references/scope.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
