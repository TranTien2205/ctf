# Walking a bin — following the links


To see the real bin state, walk the links — r2 -d does it via dmh/dmhf;
by hand: head → fd → fd → ...

## The walk

- tcache/fastbin: singly-linked — follow fd until 0 (or the mangled
  end).
- unsorted/small/large: doubly-linked — fd forward, bk backward to the
  head.

## Use

Confirm the poison landed: after corrupting fd, the walk should reach
your target in N steps.

## Falsifier

The walk diverges from the plan — the corruption didn't land where
expected; re-derive.
