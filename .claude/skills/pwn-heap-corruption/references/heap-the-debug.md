# Debugging heap corruption — the dmh loop


The loop: break before the op → dmh → run the op → dmh → diff — the
diff IS the diagnosis.

## The pattern

    r2 -d ./chal
    db <the corrupting op>
    dc
    dmh               # state before
    dc                # run the op
    dmh               # state after — diff

Each checkpoint either confirms the corruption landed or shows where
it went.
