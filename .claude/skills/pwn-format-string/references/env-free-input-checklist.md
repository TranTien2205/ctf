# Env-free input — fmtstr through argv/env/file — checklist

Companion to `env-free-input.md`.

## Checklist

- [ ] 1. Same primitive, different transport — match byte restrictions.
- [ ] 2. argv/env can't contain \x00 — pointer bytes can't be planted there.
- [ ] 3. A file-read format input can carry any byte.
