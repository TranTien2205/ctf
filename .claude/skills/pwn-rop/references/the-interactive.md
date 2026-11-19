# The interactive tail — after the shell


A fired shell needs interaction — send commands, read the flag:

    s.send(b'cat flag*\n')
    data = s.recv(4096)

## The loop

A read-eval-print loop over the socket until the flag appears — then
the hook.
