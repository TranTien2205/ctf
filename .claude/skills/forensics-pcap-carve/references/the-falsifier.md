# The falsifier — all normal traffic

Every exported object and followed stream is normal traffic → the
flag isn't in this capture's data; reclassify.

## The sub-falsifiers

- Objects exported and read — all expected content.
- Every field-carve reassembles to noise — no split flag.
- Every followed stream is benign protocol traffic.
- The DNS tunnel decode yields nothing under any suffix.
- The raw strings pass surfaces nothing flag-shaped.

## What the falsifier is NOT

- One dry channel isn't a falsifier — a field-carve on the wrong
  field is one negative among many. The class closes only when
  objects + streams + field-carves + the tunnel all yield normal.
