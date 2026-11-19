# Writing zero — the count-can't-shrink edge


Writing 0 or a very small value: the count is cumulative — by the time
%n fires, some bytes were already printed. You can't write a value lower
than the count so far.

## Steps

1. To write a low byte of 0x00 via %hhn: get the count to a multiple of
   256.
2. If the count already passed it — wrap: add 256-k padding.
3. For a full %n write of 0: impossible mid-call; do it as the FIRST
   specifier.

## Falsifier

A needed 0x00 byte can't be produced because the count already exceeded
the wrap point.
