# Detecting the ROP case — when this skill applies — checklist

Companion to `the-detection.md`.

## Checklist

- [ ] Shellcode can run (NX off or RWX): inject, don't chain.
- [ ] No IP control yet: the upstream class is the real one — return to
