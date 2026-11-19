# Hunting pop rdi — the arg0 setter — checklist

Companion to `the-pop-rdi-hunt.md`.

## Checklist

- [ ] `pop rdi; ret` — the clean one.
- [ ] `pop rdi; pop rXX; ret` — a two-pop; budget the extra qword.
- [ ] `pop rdi; <side effect>; ret` — audit the tail.
