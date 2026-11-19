# The checkpoint habit — verify each stage


After each stage, verify before composing:

- After the leak: the value is a plausible pointer.
- After the pops: the registers hold the args.
- After the call: the observable happened.

A verified stage is a floor the next stage builds on.
