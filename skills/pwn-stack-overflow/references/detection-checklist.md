# Detection â€” naming it stack corruption — checklist

Companion to `detection.md`.

## Checklist

- [ ] Observation
- [ ] `gets`, `scanf %s`, `strcpy` into a local
- [ ] `read(fd, buf, n)` where n is influenced
- [ ] crash whose faulting RIP holds your bytes
- [ ] `strcpy`/`memcpy` with computed n
- [ ] `sprintf`/`vsprintf` into a stack buffer
- [ ] Observation
- [ ] `printf(user_input)` without a length issue
- [ ] corruption into heap metadata
- [ ] the crash is in a parser, not a return
- [ ] the bound is genuinely fixed and unreachably large
- [ ] Is there a write into a stack-allocated buffer?
- [ ] Can its length exceed the buffer's allocation?
- [ ] Does the write reach the saved frame (canary â†’ saved RBP â†’ saved RIP)?
