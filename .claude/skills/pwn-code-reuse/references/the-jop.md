# JOP — jmp-gadget chains


When ret gadgets are scarce but jmp/call exist: JOP chains jump
between gadgets via a dispatcher — the "jmp [rX]" shape.

## The dispatcher

    pop rXX ; jmp [rXX]     # the dispatch: rXX points at the gadget

A table of gadget addresses in a register, walked by jmp — harder to
build, sometimes the only option.

## Falsifier

Normal ret-chains exist — prefer them; JOP is the scarcity fallback.
