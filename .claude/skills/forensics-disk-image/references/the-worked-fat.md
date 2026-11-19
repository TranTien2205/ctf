# Worked — a FAT32 deleted file

1. part_table → offset 2048.
2. fat_read list --deleted --offset 1048576 → `GONE.TXT`.
3. get /GONE.TXT → the freed chain's bytes → flag.
