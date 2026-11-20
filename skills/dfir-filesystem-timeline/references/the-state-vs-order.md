# $MFT is state, $J is order

`$MFT` records are reused and carry only the current file's times —
it cannot prove deletion order. `$UsnJrnl:$J` is the ordering source:
one record per event with reason bits. Answer "what happened in
what order" from `$J`, "what exists now" from `$MFT`.
