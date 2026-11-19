# Composing the chain — the build order


Build in this order — verify each:

1. The offset to saved rip (measured).
2. The canary's slot (if present — leaked value placed).
3. The pops + args.
4. The alignment ret (if needed).
5. The call target.
6. The ending (exit or loop).
