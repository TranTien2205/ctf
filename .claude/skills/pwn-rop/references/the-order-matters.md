# When the order matters — the dependencies


Order matters where there's a dependency: the write before its read,
the leak before its use, the pops before the call — free reordering
only among independent entries.
