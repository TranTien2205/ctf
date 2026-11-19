# Env-free input — fmtstr through argv/env/file


Like stack smashes, the format-string input can arrive via argv, an env
var, or a file read — the transport rules apply but the primitive is
unchanged.

## Steps

1. Same primitive, different transport — match byte restrictions.
2. argv/env can't contain \x00 — pointer bytes can't be planted there.
3. A file-read format input can carry any byte.

## Falsifier

None; transport only. \x00 restriction kills pointer-planting via
argv/env — need the pointer elsewhere.
