# Worked — the WAL row

1. db.sqlite + db.sqlite-wal in the image.
2. sqlite_wal frames → an un-checkpointed frame's page.
3. strings on the frame → the deleted row's flag.
