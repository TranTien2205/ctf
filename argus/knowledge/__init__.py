"""Reusable knowledge: probe ladders per class, the exploit-script registry, the
system's own corpus of chain cards harvested from confirmed findings, and an
optional read-only bridge to a prior CTF toolkit's verified chains.

The two card corpora are ranked separately and never merged. They are not the
same measurement: a card of our own is scored by the share of its declared stack
markers the target has been observed to have, and an external card by words
appearing anywhere in it. Merging them would rank a card with a long description
above a card about the right product."""
