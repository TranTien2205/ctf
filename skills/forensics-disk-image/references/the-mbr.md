# MBR — the classic partition table

The MBR (512 bytes, sig 0x55AA) holds 4 primary entries —
type+start+size. EBR chains extend logical partitions.

## part_table decodes it

part_table.py walks MBR + the EBR logical chain itself — each
partition's offset reported.
