# The table shape — the driven compare


A lookup-table check: input bytes index a table, the results are
compared — dump the table, invert the mapping.

## The dump

    pxq @ <table_addr>          # or
    ps @ <table_addr> <len>

The table's bytes + the indexing rule reproduce the check.
