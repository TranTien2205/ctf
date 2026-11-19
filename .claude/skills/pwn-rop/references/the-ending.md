# The ending — the last qword


The chain's final entry: the observable ending — a shell, a flag
print, a loop re-entry, or a clean exit.

## The options

- exit@plt — clean termination.
- main — the loop re-enters for another stage.
- A crash — acceptable IF the observable already fired.

## The gate

The printed flag goes through the hook:

    python3 tools/hooks.py pre-flag <chal> --value 'flag{...}' --source response --evidence '<excerpt>'
