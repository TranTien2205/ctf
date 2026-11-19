# The partition table — where data lives

The partition table names each volume's offset — the flag volume's
`first_lba`/`offset` is the --offset for the fs tools.

## The tools

    mmls image.dd                          # sleuthkit
    fdisk -l image.dd
    python3 tools/forensics/part_table.py image.dd   # JSON offsets

## The output

part_table emits each partition's first_lba, offset, type — the
`offset` feeds fat_read/ext_read/exfat_read's `--offset`.
