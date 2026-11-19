# The signal handler check — the trap path


A check reached via a signal/exception handler — the handler's code
is the decider; find it via the sigaction call's handler arg.
