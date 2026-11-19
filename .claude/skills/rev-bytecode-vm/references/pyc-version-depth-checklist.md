# The .pyc version problem — which marshal can read it — checklist

Companion to `pyc-version-depth.md`.

## Checklist

- [ ] Match → marshal.loads works, dis.dis works, the floor holds.
- [ ] Mismatch → either fetch that interpreter, or use a version-matched
- [ ] 1. Fetch the matching interpreter (a container, a tarball, pyenv).
- [ ] 2. `xdis` — a cross-version marshal/dis library that reads many
- [ ] 3. A decompiler targeting that version (decompyle3, pycdc).
