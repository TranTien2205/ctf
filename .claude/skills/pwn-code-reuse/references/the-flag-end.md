# The flag end — the observable landing


The chain's final target must produce observable output: a flag print,
a shell, a file read — the ending the exploit exists for.

## The endings

- system("/bin/sh") → interactive shell → cat flag.
- A win function → it prints the flag.
- execve → the shell.
- A read-chain → the flag's bytes.

## The gate

The printed flag is a candidate until the hook clears it:

    python3 tools/hooks.py pre-flag <chal> --value 'flag{...}' --source response --evidence '<excerpt>'
