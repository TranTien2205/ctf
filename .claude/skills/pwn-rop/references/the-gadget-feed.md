# Feeding the gadgets — where addresses come from


The chain's addresses come from real scans:

    python3 tools/pwn_triage.py ./chal --gadgets
    r2 -A ./chal
    /R pop rdi
    /Rj syscall

## The rule

An address not observed in the scan output does not exist — the
repository rule applies hardest here: a ROP chain is entirely made
of addresses.
