# Hunting leave — the pivot gadget


`leave; ret` = `mov rsp, rbp; pop rbp; ret` — rsp = rbp's value:

    /R leave

## The use

Set rbp to the target region (via saved-rbp slot or pop rbp); the
epilogue's leave;ret pivots rsp there — the stack pivot primitive.
