# Finding the compares — the instruction scan


    / cmp                 # instruction search
    pdf @ func | grep -E 'cmp|test|call'

Within a function, grep the disasm for the compare instructions —
the deciding one is near the verdict call.
