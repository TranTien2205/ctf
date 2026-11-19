# Boundary — the pyc-embedded-in-binary case — checklist

Companion to `classify-boundary2.md`.

## Checklist

- [ ] Extract the .pyc (pyinstxtractor, or the embedded marshal blob).
- [ ] If the check is in the .pyc → this class.
- [ ] If it's in compiled native code → rev-native-check.
