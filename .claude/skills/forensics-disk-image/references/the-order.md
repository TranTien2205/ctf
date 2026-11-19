# The extraction order — the rule

Table → live+deleted → unallocated carve → streams/slack → archives
→ sqlite → containers → firmware. Each layer's output feeds the
next; every layer read-only.
