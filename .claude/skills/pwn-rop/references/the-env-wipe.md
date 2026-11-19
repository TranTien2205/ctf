# The env wipe — when the env breaks the chain


system() needs a sane environment — a corrupted env (the chain's
side effects) can break the shell spawn.

## The check

If the shell doesn't spawn but the call reached: envp corruption —
re-derive or clean the env.
