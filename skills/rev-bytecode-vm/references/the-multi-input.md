# Multi-input checks — two reads per cmp

Some VMs read TWO flag bytes per iteration (a pair transform) —
the count of read ops halves the checked positions; the transform
mixes adjacent bytes.
