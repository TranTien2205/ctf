# Deleted and unallocated recovery

## The three places a flag hides

1. **Live files** — `fls -r` shows them; `icat <inode>` reads them. Boring,
   always check first.
2. **Deleted-but-allocated** — `fls -r` marks them `*`; the inode still
   points at blocks. `icat` pulls the bytes exactly. NTFS/exFAT keep the
   pointers; ext4 zeroes them (see below).
3. **Unallocated space** — no directory entry survives; carve by signature:
   `photorec`, `foremost`, `binwalk -e` on the unallocated partition or whole
   image.

## Per-tool quick table

| Task | Command |
|---|---|
| partition table | `mmls image.dd` |
| file listing (deleted too) | `fls -r -o <sector-offset> image.dd` |
| read inode | `icat -o <offset> image.dd <inode> > out` |
| journal (NTFS/ext) | `icat ... $Extend/$UsnJrnl` ; ext: `ils`, `jls` |
| signature carve | `foremost -i image.dd -o out/` ; `photorec` |
| ADS (NTFS streams) | `fls -m`, `icat image.dd <inode>:<stream>` |
| mount live | `mount -o ro,loop,offset=$((start*512)) image.dd /mnt` |

## ext4 delete is different

On ext4 the inode's block pointers are zeroed on delete — `fls` shows the
filename but `icat` returns zeros. The recovery path is signature carving
(photorec/foremost) or journal mining, NOT icat. Record which filesystem
`mmls`/`fsstat` reports before choosing.

## Hidden partitions

`mmls` gaps or a partition type "unallocated" spanning the answer region is
the classic hide. Carve the WHOLE image when a listed partition holds
nothing interesting — the flag often lives between them.
