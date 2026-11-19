# Field manual variant — the alternate 15-minute card

## The seven-question card

```
1. WHICH generator?   lcg / lfsr / mt19937 / xorshift128 / seed / CSPRNG(out)
2. HOW MANY outs?     3 / 6 / req / 2w / 624 / 4 / window
3. RAW + CONSEC?      ints, no gaps, no reseed
4. WHICH params?      m | a,c | taps,width | low-bits | seed window
5. WHICH attack?      the param-known column
6. WHICH command?     crypto_attack.py <id> / xorshift128.py
7. VERIFY?            predict == held-back
```

## The five-flag map

```
--outputs  comma ints (LCG/MT)
--outs     comma ints (xorshift128)
--bits     comma 0/1 (LFSR)   --keystream-hex  --bits-file
--modulus  LCG m              --a --c          the params
--low-bits DROPPED b          --taps --width   LFSR params
--count    next n             --outputs-file/--bits-file/--in/--json
```

## The five-trap card

```
1. --low-bits = DROPPED (not kept)
2. --taps = 1-indexed-LSB
3. outputs RAW ints — float/mod/randint normalize
4. Math.random = xorshift128+ NOT xorshift128
5. 624 exact / 2w exact / 3/6/4 floors
```

## The four-record card

```
predict==held → post-probe --verdict confirms --evidence 'predict==held' --response <bytes>
flag{        → pre-flag --value 'flag{...}' --evidence '<bytes>'
solve        → classify_solve → field-notes confirmed
falsify      → attempts + reopen_if → decide.py rung
```

## The two-status card

```
catalogue class — no local chains — the corpus is the field procedure
predict==held is the only proof
```
