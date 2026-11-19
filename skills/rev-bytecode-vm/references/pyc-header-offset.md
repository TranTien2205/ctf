# 12 vs 16 byte headers

3.7+ uses a 16-byte header (magic+flags+hash); older uses 12. marshal.loads(d[16:]) or d[12:] — the wrong offset fails before the code object parses.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.
