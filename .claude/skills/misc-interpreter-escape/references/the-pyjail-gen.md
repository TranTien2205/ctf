# pyjail_gen — the corpus filter

`python3 tools/pyjail_gen.py --banned w1 w2 --banchars "()'"` filters
the escape corpus to the shapes surviving the bans — and emits a
chr-join for any banned attribute name.

## The filter

--banned/--banchars -> the surviving shapes + a chr-join.
