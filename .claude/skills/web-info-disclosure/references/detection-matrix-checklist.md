# Detection matrix — which channel is open — operational checklist

One table: the probe, the positive answer, the file that owns it.

## Checklist

- [ ] Baseline the catch-all before ANY of these reads.
- [ ] Run the bounded list once; read every response body.
- [ ] Route each hit to its owning file.

## Abort conditions

- Status is not the discriminator — content is.
- Each channel has its own falsifier; a closed channel doesn't close the class.

## Falsifier

Falsifier — the whole bounded list returns catch-all content: no channel is open.

## Cross-references

`bounded-sweep.md` · `catchall-falsifier.md`
