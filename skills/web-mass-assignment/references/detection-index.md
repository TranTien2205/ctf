# Detection index — the detection question to the detection module

| If the question is... | Open |
|---|---|
| where the writable surface lives | `detection-surface.md` |
| the field inventory, exhaustively | `detection.md` → `field-dictionary.md` |
| which binder is running | `detection.md` — binder fingerprint |
| the endpoint priority | `detection-matrix.md` |
| the carrier matrix | `detection-matrix.md` → `carrier-shapes.md` |
| the probe order | `detection.md` → `workflow.md` |
| the bundle/sourcemap recon | `detection.md` → `bundle_miner` usage |
| what falsifiers remain open | `falsifiers.md` → `falsifiers-deep.md` |
| the endpoint-vs-binder map | `detection.md` → `per-endpoint.md` |
| the read-back protocol | `readback-protocol.md` |
| the tool's interface | `workflow.md` → `binding_probe` section |

## The detection pipeline

```
1. endpoint map    → bundle_miner + route enumeration
2. field map       → GETs + bundle + errors + docs
3. binder type     → stack headers + error shapes
4. carrier matrix  → which content-type/method reaches which binder
5. probe order     → widest binder first, then falsifier-driven
```

## The detection artifacts

| Artifact | Where it lands |
|---|---|
| endpoint list | `notes.md` — the binder surface |
| field list | `notes.md` — the writable surface |
| binder fingerprint | `notes.md` — the grammar |
| falsifier map | `field-notes.md` — the dead cells |
| live-cell matrix | `field-notes.md` — the remaining probes |

## The cheap-first order

1. `GET /api/me` — the field inventory, free;
2. `bundle_miner` — the endpoint map, free;
3. wrong-typed probe — the schema leak, one request;
4. control + canary — the first real probe, two requests;
5. `PATCH` + nested — the tunnels, two requests each.

The cheapest detection is reading; the most expensive is blind
payload-firing.
