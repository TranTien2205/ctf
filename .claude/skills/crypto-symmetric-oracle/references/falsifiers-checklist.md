# Falsifiers — the observations that close each attack — checklist

Every attack in this class has a specific observation that kills it. Check
the falsifier before investing a loop; the falsifier is cheaper than the
attack.

## Checklist

- [ ] Run the cheapest falsifier probe FIRST (usually one request or one grep).
- [ ] If it fires, record the negative and route out — do not start the loop.
- [ ] If it does not fire, the attack applies; run it.
- [ ] A falsifier that fires mid-loop means the mechanism was misread — stop,

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
