# tools/forensics/part_table.py

MBR(+EBR)/GPT — emits first_lba/offset/type JSON per partition.

## The call

    python3 tools/forensics/part_table.py ...

Check `--help` for the real flags; `--selftest` proves it offline where offered. See the-workflow.md for where it sits in the extraction order.
