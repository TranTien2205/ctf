# Read vs write — the branch in the primitive — checklist

Companion to `the-read-vs-write-choice.md`.

## Checklist

- [ ] Need a value (canary, base, address)? → read.
- [ ] Need to redirect execution? → write.
- [ ] Often both: the read feeds the write's value/target.
