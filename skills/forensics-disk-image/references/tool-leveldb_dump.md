# tools/forensics/leveldb_dump.py

LevelDB .log/.ldb — WriteBatch records incl deletions; inline snappy.

## The call

    python3 tools/forensics/leveldb_dump.py ...

Check `--help` for the real flags; `--selftest` proves it offline where offered. See the-workflow.md for where it sits in the extraction order.
