# Theory index — the conceptual files and what each explains

## The "why" files

| File | What it explains |
|---|---|
| `theory.md` | the root causes — the contract's limits |
| `theory-deep.md` | the deep root causes — the trust-inversion, the shared-everything, the atomicity, the immutability, the attribution |
| `theory-map.md` | the limit → the classes it produces |
| `theory-catalogue.md` | the per-class root-cause |

## The "how" files

| File | What it explains |
|---|---|
| `mechanism.md`/`mechanism-deep.md` | the EVM execution model |
| `evm-primitives.md` | call/delegatecall/staticcall/selfdestruct/create |
| `mechanism-map.md`/`mechanism-index.md`/`mechanism-catalogue.md` | primitive → bug class |
| `storage-collision-deep.md` | the slot-layout model |

## The "what" files

| File | What it explains |
|---|---|
| detection*.md | the signals/the predicate/the surface |
| `attack-shapes.md`/per-*.md | the maps |
| the bug files | each class's mechanism + exploit |
| payload-*.md | the call/contract shapes |
| evidence-*.md | the proof |
| workflow*.md | the order |

## The conceptual stack

```
the EVM model (mechanism-*) → the primitives (evm-primitives)
  → the misuses (the bug files) → the predicate selection (detection-*)
  → the exploit (payload-*, exploitation-*) → the proof (evidence-*)
  → the order (workflow-*)
```

## The catalogue-theory note

The theory is published EVM knowledge — the model is standard. The local
experience (what the corpus got wrong, what the chain actually did) is in
`../field-notes.md` — a `catalogue` class's theory is the starting point, not
proof.
