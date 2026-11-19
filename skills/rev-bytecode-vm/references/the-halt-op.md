# The halt — the program's end

The VM's halt/exit op ends the program — decode stops there.

## The win/lose halt

Two halts: `win` prints accepted, `fail` prints rejected — the
program's cmp ops jump to one or the other. The path to `win` is
the accepted-input path.
