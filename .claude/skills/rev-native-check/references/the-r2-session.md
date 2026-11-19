# The r2 session — the command sequence


    r2 -A ./chal          # analyze all
    afl                   # functions
    iz                    # strings
    axt @ str.x           # xrefs to a string
    pdf @ main            # disassemble
    / str                 # search for an instruction pattern
    s <addr> ; pd 30      # seek + disassemble a window

The session's rhythm: inventory → locate → read → verify.
