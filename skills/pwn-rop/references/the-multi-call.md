# Multiple calls — the sequence


A chain performing several calls — leak + plant + call:

    [leak recipe] [write recipe] [the call] [the ending]

Each call's "return" is the next chain entry — one long ret-walk.

## The dependencies

A plant precedes its read; a leak precedes its use — the partial
order is the dependency graph.
