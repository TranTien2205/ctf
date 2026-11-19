# The chain card — recording the solved heap


After the flag: write the card so the next heap challenge recalls the
path.

## The card

- signals: the menu ops + the abort/behavior that named the class.
- first_confirming_probe: the free+dangling-read that proved UAF or
  the double-free that proved dup.
- the chain: version → primitive → leak → corrupt → write → fire.
- traps: the version gate, the key check, safe-linking, the slot cap.
- blast_radius: heap corruption destabilizes the service — a misfired
  write crashes it.
