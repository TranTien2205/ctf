# The wrong offset — the most common fail


The chain lands but rip isn't your gadget: the offset was wrong —
re-measure with the cyclic tool on the real input.

## The recheck

    python3 tools/pwn_cyclic.py <n>
    # run, capture the crash value
    python3 tools/pwn_cyclic.py --find <value>
