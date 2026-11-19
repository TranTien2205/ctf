# The flags map — the branch decoder — map

Companion to `the-flags-map.md`.

| Branch | Reads | Meaning |
|---|---|---|
| jz/je | ZF | equal |
| jnz/jne | !ZF | different |
| ja | !CF & !ZF | unsigned above |
| jb | CF | unsigned below |
| jg | !ZF & SF==OF | signed greater |
| jl | SF!=OF | signed less |
| jge | SF==OF | signed greater-equal |
| jle | ZF | SF!=OF | signed less-equal |
