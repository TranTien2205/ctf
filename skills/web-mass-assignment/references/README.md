# web-mass-assignment — references

Mass assignment / parameter binding. Use after the router or classify names
this class; start with the first probe and record the expected signal. Do
not use it as proof of a finding. **Catalogue class** — nothing in this
toolkit has solved one yet; everything here is standard published knowledge.

## The one-question index

| If you need... | Open |
|---|---|
| the runbook | `field-manual.md` |
| the 30-second version | `quick-reference.md` |
| the first sixty minutes | `first-hour.md` |
| the mechanism internals | `mechanism.md` → `mechanism-deep.md` |
| the endpoint map | `detection.md` → `per-endpoint.md` |
| the field inventory | `field-dictionary.md` → `field-dictionary-deep.md` |
| the carrier shapes | `carrier-shapes.md` → `carrier-shapes-deep.md` |
| the probe protocol | `readback-protocol.md` → `readback-protocol-deep.md` |
| the binder per stack | `framework-matrix.md` → `framework-matrix-deep.md` |
| the exploit shapes | `exploitation.md` → `exploitation-deep.md` |
| the attack chains | `attack-shapes.md` → `multi-step-chains.md` |
| what kills the class | `falsifiers.md` → `falsifiers-deep.md` |
| honest dead ends | `negative-results.md` → `negative-results-deep.md` |
| the class boundary | `class-boundary.md` |
| when it breaks | `edge-cases.md` → `edge-cases-deep.md` |
| what goes wrong | `common-mistakes.md` → `common-mistakes-deep.md` |
| when it fails | `troubleshoot.md` → `troubleshoot-deep.md` |
| past the filters | `evasion.md` → `evasion-deep.md` |
| the checks it passes | `per-check.md` |
| the vectors | `per-vector.md` |
| the routes | `per-route.md` |
| the surfaces | `per-surface.md` → `detection-surface.md` |
| the boundaries | `per-boundary.md` |
| the mechanisms | `per-mechanism.md` → `mechanism-index.md` |
| the payload set | `payload-variants.md` → `extended-corpus.md` |
| the field names | `field-dictionary.md` → `extended-corpus.md` |
| the engagement flow | `workflow.md` → `workflow-deep.md` |
| the step-by-step | `workflow-checklist.md` → `checklist.md` |
| the decision matrix | `detection-matrix.md` |
| the detection order | `detection-index.md` → `detection-checklist.md` |
| why it exists | `theory.md` |
| terms | `glossary.md` |
| mistakes to avoid | `anti-patterns.md` |
| real incidents | `real-world-cases.md` |
| CTF shapes | `case-studies.md` |
| first-time reader | `onboarding.md` |
| what must be true | `preconditions.md` |
| the FAQ | `common-questions.md` |
| the shortest form | `summary.md` |
| verified solves | `verified-chains.md` (none — catalogue) |
| the original anchor | `binding-shapes.md` |

## The mechanism map

| Mechanism | Module |
|---|---|
| merge-all binder | `mechanism.md` — merge-all section |
| kwargs signature | `mechanism-deep.md` — kwargs section |
| allowlist | `mechanism.md` — allowlist section |
| strict schema | `mechanism-deep.md` — strict-schema section |
| deep merge / nested tunnel | `mechanism-deep.md` — deep-merge section |
| nested association | `mechanism-deep.md` — association section |
| discriminator switch | `mechanism-deep.md` — discriminator section |
| type coercion | `mechanism-deep.md` — coercion section |
| method permutation | `per-mechanism.md` — mechanism I |
| serializer-hidden | `per-mechanism.md` — mechanism J |

## The evidence pipeline

1. control request — the documented body;
2. canary request — ONE extra field;
3. read-back — `GET` through a DIFFERENT endpoint;
4. decision exercise — hit the gate the field controls.

`readback-protocol.md` is the formal protocol; `evidence-rules.md` is
the confirm/falsify standard; `falsifiers.md` is the kill-map.

## The tool

`tools/web/binding_probe.py` — the field-matrix runner:

```bash
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

Default field set: `role`, `admin`, `is_admin`, `isAdmin`, `debug`,
`permissions`, `group`, `verified`, `is_staff`. `--fields` overrides;
`--method GET` tests query; `--headers` carries auth.

General guidance — no solved chain in this toolkit yet.
