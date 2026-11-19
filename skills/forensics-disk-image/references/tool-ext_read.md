# tools/forensics/ext_read.py

ext2/3/4 — superblock->GDT->inode tables; extents + direct blocks.

## The call

    python3 tools/forensics/ext_read.py ...

Check `--help` for the real flags; `--selftest` proves it offline where offered. See the-workflow.md for where it sits in the extraction order.
