# The falsifier — nothing but expected content

Live files + deleted entries + unallocated carving yield only
expected OS content → the flag isn't in this image; reclassify.

## The sub-falsifiers

- The fs layer intact but nothing deleted → check unallocated.
- Unallocated clean → check streams/slack/archives.
- Archives/sqlite/containers clean → check stego (pixel hides) or
  reclassify — the flag may not be in the image at all.
- An encrypted region with no recoverable key → the flag is locked,
  not findable from the image alone.

## What the falsifier is NOT

- One dry layer isn't a falsifier — keep walking the extraction
  order. The class closes only when EVERY layer yields expected
  content.
