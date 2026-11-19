# Write shapes — byte/word/page granularity — checklist

Companion to `the-write-shape.md`.

## Checklist

- [ ] Bug gives | Reach | Techniques
- [ ] 1 byte | size LSB, flag bits | off-by-null
- [ ] 4-8 bytes | full size word | size-forge
- [ ] 8 bytes on a freed chunk | fd/key | poison/key-clear
- [ ] bounded OOB | specific struct fields | targeted corruption
- [ ] arbitrary | anything | all
