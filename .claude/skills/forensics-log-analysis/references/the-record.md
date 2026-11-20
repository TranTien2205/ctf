# Recording — what to log

- The file(s) analysed + their line counts + timestamp range.
- The field(s) distributed and the top-N result.
- The anomalous line, verbatim, with its line number.
- The window context around it.
- The count/baseline making it anomalous.

A finding without the denominator isn't reproducible — record
the baseline beside the hit so the anomaly can be re-derived.

## The evidence packet

- File name + wc -l + timestamp range.
- The distribution command + its top output.
- The anomalous line, verbatim, with its number.
- The window command + the context lines.
- The count comparison (this IP vs the peers).
