# When fmtstr is THE answer vs a stepping stone


Sometimes fmtstr solves the challenge outright (flag in memory, direct
GOT→system); sometimes it's just the leak for a bigger chain.

## Cases

- Flag in readable memory → %s read, done.
- Flag needs exec → %n redirect to system/execve-chain.
- A coexisting stack overflow → fmtstr leaks canary/base, smash exploits.

## The rule

Cheapest-first: try the %s flag-read before building a write chain.
