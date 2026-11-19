# The frame-pointer chain — leave;ret deep


leave;ret on a controlled rbp: rsp = rbp; rbp = [rsp]; rsp += 8; ret —
rsp moves to rbp, the ret pops from there.

## The double-pivot

    set rbp = region; the epilogue's leave;ret lands rsp there.

The classic use: pivot into a buffer the overflow can't directly
control the rip of — the second write's landing.
