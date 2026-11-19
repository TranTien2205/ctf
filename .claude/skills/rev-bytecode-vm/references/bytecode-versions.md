# Versioned instruction sets

Each CPython version's ops differ (3.11 adaptive ops) — dis output is only valid for the unmarshalling version.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.
