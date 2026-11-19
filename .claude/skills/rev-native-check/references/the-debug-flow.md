# The debug flow — the r2 -d session


    r2 -d ./chal
    dcu main                # to main
    db sym.imp.strcmp       # at the compare
    dc                      # run
    drr                     # the operands resolved
    ps @ rdi ; ps @ rsi     # both sides

The fastest dynamic answer.
