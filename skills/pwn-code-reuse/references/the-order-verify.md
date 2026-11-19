# Verifying order — the chain's sequence


The chain's correctness is order-sensitive: a pop before its arg slot,
a call before its pops — sequence errors are the most common failure.

## The audit

Write the chain; simulate it on paper: each ret consumes the next
qword — walk the sequence, check the register state at each step.
