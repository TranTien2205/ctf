# The entry chain — e->next walking


tcache bins are singly-linked by e->next — the alloc takes the head and
sets head = e->next (de-mangled on 2.32+).

## The walk

    head = entries[i]
    alloc: entries[i] = reveal(head->next)
    return head

## Falsifier

The chain is inconsistent (a cycle or a dead end): the walk aborts or
loops — the poison must produce a plausible chain.
