# Saved-FP overwrite via %n — frame pivot


Overwriting saved RBP with a controlled value, then letting the epilogue's
'leave; ret' run, pivots RSP to your buffer — an alternative to direct
ret-addr overwrite.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| saved RBP's stack addr known | pivot target | %n to it |
| a controlled buffer elsewhere | pivot destination | the staged chain |

## Steps

1. Leak the saved RBP's stack address.
2. Write your staged-buffer address into saved RBP via %n.
3. On 'leave; ret': RSP=RBP (your buffer), then ret pops its first qword.
4. Your staged buffer holds the ROP chain.

## Falsifier

-fomit-frame-pointer build (no saved RBP) or no known-address writable
buffer: no pivot.
