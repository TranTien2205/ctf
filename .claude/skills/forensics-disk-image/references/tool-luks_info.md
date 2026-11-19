# tools/forensics/luks_info.py

LUKS header — cipher/mode/hash, payload offset, live key slots, KDF cost.

## The call

    python3 tools/forensics/luks_info.py ...

Check `--help` for the real flags; `--selftest` proves it offline where offered. See the-workflow.md for where it sits in the extraction order.
