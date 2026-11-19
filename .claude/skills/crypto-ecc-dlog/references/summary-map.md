# Summary map — the corpus laid out as one diagram

```
                        crypto-ecc-dlog
                              │
        ┌─────────────┬───────┴───────┬─────────────┐
        │   nonce     │     dlog      │   defect    │
        │  (sigs)     │  (h = g^x)    │  (curve)    │
        └──────┬──────┴───────┬───────┴───────┬─────┘
               │              │               │
      ┌────────┼─────┐   ┌────┼────┐    ┌─────┼─────┬──────┐
      │        │     │   │    │    │    │     │     │      │
   reuse   hnp-ecdsa hnp PH  bsgs  smooth smart sing invalid
```

## The files behind each node

| Node | Files |
|---|---|
| nonce | `per-family-nonce.md`,`ecdsa-nonce-reuse*.md`,`hnp-ecdsa*.md`,`hnp*.md` |
| dlog | `per-family-dlog.md`,`pohlig-hellman*.md`,`bsgs*.md`,`smoothness*.md` |
| defect | `per-family-curve-defect.md`,`smart-*.md`,`singular-*.md`,`invalid-*.md` |

## The discipline layer (all nodes)

`detection*` `workflow*` `payload-*` `verify*` `evidence*`
`boundary-cases*` `per-boundary*` `per-condition*` `per-check*`
`falsifiers*` `per-falsifier` `troubleshoot*` `common-mistakes*`
`anti-patterns*` `evasion*` `edge-cases*` `negative-results*`
`checklist*` `operator-*` `field-*` `verified-chains*`
`case-studies*` `worked-examples*` `scenarios*` `real-world-cases*`
`multi-step-chains*` `lead-grammar*` `class-boundary*`
`theory*` `mechanism*` `glossary*` `summary*` `closing-*`
`onboarding*` `first-hour*` `quick-reference*` `map-index*`
