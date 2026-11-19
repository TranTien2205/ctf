# Verifying the flag — the hook


The produced flag goes through the gate:

    python3 tools/hooks.py pre-flag <chal> --value 'flag{...}' --source response --evidence '<excerpt>'

The evidence is the binary's output containing it.
