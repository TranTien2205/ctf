# GPT — the modern partition table

GPT: a protective MBR + the header at LBA1 + the entry array —
each entry a 16-byte type GUID + first/last LBA.

## part_table decodes it

part_table.py parses GPT headers and emits first_lba/offset/type.
