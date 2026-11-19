# Borrowed size bytes — using existing data as headers


A fake chunk needs a size field — existing memory contents often serve:
any qword whose value is aligned and >= 0x20 can be a "size".

## The scan

Read the target region for a qword looking like a size — aim the fake
chunk so that qword lands at size-offset.

## Falsifier

No plausible size qword exists near the target: the fake needs planted
bytes.
