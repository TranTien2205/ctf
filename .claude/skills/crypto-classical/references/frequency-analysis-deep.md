# Frequency analysis deep — the letter statistics, annotated

## The English frequencies — the `σ`-preserved shape

```
E 12.7   T 9.1   A 8.2   O 7.5   I 7.0   N 6.7   S 6.3   H 6.1
R 6.0    D 4.3   L 4.0   U 2.8   C 2.8   M 2.4   W 2.4   F 2.2
G 2.0    Y 2.0   P 1.9   B 1.5   V 1.0   K 0.8   J 0.15  X 0.15
Q 0.10   Z 0.07
```

The order `ETAOIN SRHLD CUMWFG YPB VKJXQZ` is what `σ` preserves — `σ(E)` is
the top `ct` letter.

## The monoalphabetic read — the `σ` skeleton

`σ(E)` top, `σ(T)` next, `σ(A)` third, ... — rank the `ct` letters; the rank
order approximates `σ⁻¹`. The anneal refines it — the frequency is the
*initialization*, not the answer.

## The digraphs/trigraphs — the `σ` anchors

`TH`,`HE`,`IN`,`ER`,`AN` and `THE`,`AND`,`ING`,`ION` — `σ` preserves them as
`σ(TH)` etc. A `ct` trigraph frequency table anchors `σ` — `σ(THE)` is the
top `ct` trigraph.

## The polyalphabetic flatten — IC ~0.038

The `L`-coset mix flattens the `ct` freq toward uniform — no `ct` letter is
much commoner. Per-coset, the IC returns to ~0.066 — each coset is a Caesar.

## The transposition preservation — IC ~0.05-0.066

`π` preserves the *multiset* — English letter counts but scrambled order —
the freq is English, the text is garbage. The digraphs are *broken* — `TH`
isn't `σ(TH)` because `T` and `H` are permuted apart.

## The IC — the collision probability

`IC = Σ n_i(n_i-1)/N(N-1)` — the mono/poly split: ~0.066 monoalpha/`π`,
~0.038 polyalpha.
