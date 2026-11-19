# The chain card — recording the solved heap — checklist

Companion to `heap-the-chain-card.md`.

## Checklist

- [ ] signals: the menu ops + the abort/behavior that named the class.
- [ ] first_confirming_probe: the free+dangling-read that proved UAF or
- [ ] the chain: version → primitive → leak → corrupt → write → fire.
- [ ] traps: the version gate, the key check, safe-linking, the slot cap.
- [ ] blast_radius: heap corruption destabilizes the service — a misfired
