# SQLite artifacts — the deleted-row story

Deleted rows survive in freeblocks/freelist pages until VACUUM —
`sqlite_carve.py` emits them with source=freeblock|freelist|unallocated.

## The WAL trap

A -wal beside the db: DO NOT open the db — opening checkpoints the
WAL and destroys un-checkpointed rows. Read the WAL directly:

    python3 tools/forensics/sqlite_wal.py db-wal frames
    python3 tools/forensics/sqlite_journal.py j.db-journal
