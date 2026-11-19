# Counting the alignment — the qword arithmetic


The call's entry rsp = the overwrite's rsp + (entries so far × 8).

## The rule

Count the qwords from the landing to the call: if the call's entry
rsp isn't 16-aligned, insert a ret. rop_chain.py does this
arithmetic; a hand chain does it manually.

## The tell

movaps on [rsp+...] inside the called function = off by 8.
