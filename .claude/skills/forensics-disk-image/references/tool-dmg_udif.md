# tools/forensics/dmg_udif.py

Apple UDIF .dmg — koly trailer -> mish block tables -> zlib/bzip2 chunks.

## The call

    python3 tools/forensics/dmg_udif.py ...

Check `--help` for the real flags; `--selftest` proves it offline where offered. See the-workflow.md for where it sits in the extraction order.
