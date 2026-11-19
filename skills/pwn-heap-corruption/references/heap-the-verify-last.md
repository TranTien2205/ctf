# The last verification — before the commit


The run's final check: the flag through the hook, the chain card
written, the field-notes entry filed — the solve becomes recall.

## The steps

    python3 tools/hooks.py pre-flag <chal> --value 'flag{...}' --source response --evidence '<excerpt>'
    python3 tools/classify_solve.py --chain <id>

A solve that isn't carded is one the next challenge re-derives from
zero.
