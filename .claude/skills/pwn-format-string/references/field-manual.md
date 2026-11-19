# Field manual — the condensed runbook

1. printf-family call whose format arg is your input → open.
2. %p.%p.%p → the leak confirms the primitive.
3. AAAA.%N$p → the arg offset.
4. Read path: %p words = stack dump; %s at planted ptr = arb-read.
5. Write path: %n/%hn/%hhn at planted ptr = arb-write.
6. Targets: GOT (partial RELRO), ret-addr (stack addr known), hook
   (glibc ≤2.34).
7. Redirect → the call/return/alloc fires the target → flag.
