# The ret sled — the alignment hedge


Several `ret` gadgets in sequence — a sled: rsp walks through them,
harmlessly landing on the real work — a hedge when alignment is
uncertain.

## The use

    [ret][ret][ret][the call]

The extra rets cost qwords but buy alignment insurance.
