# Reading a null result — when the leak reads 0


A dangling read returning 0 doesn't mean no leak — it means the field
wasn't populated: the chunk was the bin's tail (fd=0) or the field
was zeroed.

## Check

- Try a different freed chunk — a mid-bin one has live fd.
- A bin-tail fd=0 is itself information: the chunk was last freed.

## Falsifier

Every read returns 0 consistently: the objects are calloc'd or the
slots are cleared — no stale-data channel.
