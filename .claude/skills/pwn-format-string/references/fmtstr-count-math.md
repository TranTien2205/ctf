# Count math — computing the width for each %n


The value a %n writes equals the chars printed so far. Work backwards
from each target byte.

## The arithmetic

    want byte = 0x41 (65)
    printed so far = 0
    need %65c then %hhn  →  writes 65 = 0x41

    want next byte = 0x80 (128)
    printed so far = 65
    need %63c then %hhn → 65+63 = 128 = 0x80

    want 0x20 but count already 0x90:
    wrap: %(0x120-0x90)c = %144c → count 0x120 → low byte 0x20

## Rules

- %Nc adds N to the count.
- %hhn writes count & 0xff; %hn count & 0xffff; %n count & 0xffffffff.
- Negative widths aren't expressible — wrap mod the width instead.

## Falsifier

The width needed exceeds the output cap or the numeric limit: split into
%hn pairs or reorder.
