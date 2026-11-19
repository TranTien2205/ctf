# The complete chain — all stages


The full dynamic-binary exploit, end to end:

    <padding>
    [pop rdi][puts@got]      # the leak
    [puts@plt]
    [main_addr]              # restart
    <second overflow's padding>
    [pop rdi][binsh]         # the real chain
    [ret]
    [system]
    [exit]

Two overflows, one exploit — the canonical two-stage.
