# The disk-image workflow — extraction order

A disk/filesystem image is the handout; the flag is deleted,
unallocated, or hidden in a file the OS pretends is gone.

## The order

1. Partition table — `mmls`/`fdisk -l` or
   `python3 tools/forensics/part_table.py image.dd` (emits
   first_lba/offset/type JSON — feed --offset into the volume tools).
2. Live+deleted files — `fls -r` (sleuthkit marks deleted `*`), or
   `fat_read.py list --deleted` / `ext_read.py ls /` /
   `exfat_read.py list`.
3. Pull a deleted entry — `icat inode` or the reader's `get /PATH`.
4. Carve unallocated — `photorec`/`foremost`, or
   `tools/forensics/carve_scan.py`.
5. Streams/slack — NTFS ADS, $UsnJrnl, slack space, swap.
6. Archives inside — cpio/zip/tar/rar/7z/iso/git objects.
7. SQLite artifacts — freeblocks/WAL/journal deleted rows.
8. Container images — qcow2/vhd/vmdk/dmg/e01 → flat first.
9. Firmware filesystems — cramfs/jffs2/squashfs/uImage.

## The rule

Read-only always; evidence = recovered bytes; a file listing never
read is recon.

## Per-layer detail

- **Table.** part_table/fdisk/mmls — the offsets that feed every
  later --offset. Skip it on a bare-volume image.
- **Listing.** fls -r or the fs reader's list — live AND deleted;
  `*` or the deleted-set flag marks the recoverable entries.
- **Pull.** icat inode / get /PATH — the freed chain's bytes while
  the metadata still links them.
- **Carve.** photorec/foremost/carve_scan over unallocated — magic
  bytes bound the carve; the carved file must parse.
- **Streams/slack.** NTFS ADS (`fls -m`, named-stream icat), file
  slack past EOF, $UsnJrnl records, pagefile/hibernate.
- **Archives.** cpio/zip(local_only)/tar(trailer)/rar/7z/iso/git
  dangling — each member listed then extracted.
- **SQLite.** freeblock/freelist/unallocated cells; -wal frames and
  -journal pre-images — never open the live db when a -wal exists.
- **Containers.** qcow2/vhd/vmdk/dmg/e01 dump to flat, then the
  same chain.
- **Firmware.** cramfs/jffs2/squashfs/uImage — the embedded fs
  walked locally.

## The stop condition

The flag-bearing bytes are recovered and verified — the flag
through hooks.py pre-flag with the recovered content as evidence.
