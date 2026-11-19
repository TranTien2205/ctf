# .NET obfuscation — names and flow

Obfuscators rename TypeDefs/MethodDefs and tangle the flow — but
the #US heap still holds the literals, and the IL still computes.

## The route

Follow data flow to the check, not names — the ldstr feeding a
compare is the expected value regardless of names.
