# The FAT-deleted file

Delete marks the dir entry's first byte 0xE5 and frees the cluster
chain — `list --deleted` shows them; `get /PATH` reads the freed
chain while the FAT still links it.
