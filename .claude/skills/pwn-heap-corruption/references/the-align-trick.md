# The 0x7f alignment trick — fake chunk sizes


A byte of 0x7f before a target makes target-0x18 look like a size-0x70
chunk header — the classic fastbin-dup-into-hook trick (the preceding
libc bytes are often 0x7f).

## The use

Fake chunks can be "found" in existing data whose bytes happen to form
a sane size — scan the target region for plausible preceding bytes.

## Falsifier

No preceding byte forms a valid size for the bin you need: the
found-fake doesn't exist — plant your own.
