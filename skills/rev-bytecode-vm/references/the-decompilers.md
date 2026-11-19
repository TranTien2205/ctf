# Decompilers — uncompyle6/decompyle3


uncompyle6/decompyle3 cover old Python only (up to ~3.8) — for
3.9+ they're incomplete; the stdlib dis fallback always works on the
installed version.

## The rule

dis is the floor; decompilers are a convenience when the version
matches.
