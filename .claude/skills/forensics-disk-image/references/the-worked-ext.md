# Worked — an ext4 carve

1. ext_read ls / → a deleted-named file, empty inode.
2. carve_scan on unallocated → a PNG magic → carved.
3. The carved PNG parses → flag inside.
