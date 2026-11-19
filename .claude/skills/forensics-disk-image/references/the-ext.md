# ext2/3/4 — the Linux volume

ext: superblock → GDT → inode tables → i_block or ext4 extents —
the directory walk lists live entries.

## The tool

    python3 tools/forensics/ext_read.py fs.img ls /
    python3 tools/forensics/ext_read.py fs.img get /path

## The delete limit

ext4 zeroes inode block pointers on delete — fls/ext_read show the
name but the data is gone from the inode; carve by signature, or
the journal.
