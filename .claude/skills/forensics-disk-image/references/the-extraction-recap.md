# The extraction recap — the whole route

## The order, end to end

1. Hash the image; keep it read-only.
2. `file` + `xxd` the first sector — the format.
3. part_table/mmls/fdisk — the partition offsets.
4. The fs reader for the volume type — list live + deleted.
5. Pull deleted entries (icat / get) before carving.
6. Carve unallocated by signature; verify the parse.
7. NTFS: named streams + $UsnJrnl + slack.
8. Archives inside: zip local_only, tar trailer, git dangling,
   cpio/rar/7z/iso members.
9. SQLite: freeblock/freelist/unallocated + -wal/-journal.
10. Containers: qcow2/vhd/vmdk/dmg/e01 → flat → the same chain.
11. Firmware: cramfs/jffs2/squashfs/uImage.
12. The flag recovered → verify → hooks.py pre-flag.

## The one-line rule

Read-only; the flag is recovered bytes; a listing is recon.
