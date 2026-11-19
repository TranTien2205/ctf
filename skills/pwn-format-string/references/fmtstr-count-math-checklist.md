# Count math — computing the width for each %n — checklist

Companion to `fmtstr-count-math.md`.

## Checklist

- [ ] %Nc adds N to the count.
- [ ] %hhn writes count & 0xff; %hn count & 0xffff; %n count & 0xffffffff.
- [ ] Negative widths aren't expressible — wrap mod the width instead.
