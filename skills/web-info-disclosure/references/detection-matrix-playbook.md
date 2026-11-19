# Detection matrix — which channel is open — playbook

One table: the probe, the positive answer, the file that owns it.

## Ordered playbook

1. Baseline the catch-all before ANY of these reads.
2. Run the bounded list once; read every response body.
3. Route each hit to its owning file.

## Falsifier

Falsifier — the whole bounded list returns catch-all content: no channel is open.
