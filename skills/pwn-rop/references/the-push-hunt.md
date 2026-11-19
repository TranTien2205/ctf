# Hunting push — the stack writer


    /R push

`push rX; ret` writes a register's value onto the stack — a stack-
targeted write or the setup for a `pop` into a needed register's
value.
