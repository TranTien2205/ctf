# When fmtstr is THE answer vs a stepping stone — checklist

Companion to `when-fmtstr-is-the-answer.md`.

## Checklist

- [ ] Flag in readable memory → %s read, done.
- [ ] Flag needs exec → %n redirect to system/execve-chain.
- [ ] A coexisting stack overflow → fmtstr leaks canary/base, smash exploits.
