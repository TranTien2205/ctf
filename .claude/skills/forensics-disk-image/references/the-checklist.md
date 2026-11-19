# The checklist

- [ ] Image mounted/kept read-only
- [ ] Partition table read, offsets named
- [ ] fs type identified, the right reader used
- [ ] Deleted entries listed, pulled
- [ ] Unallocated carved by signature
- [ ] Streams/slack/archives/sqlite checked
- [ ] The flag-bearing bytes recovered
- [ ] Flag through the hook

## Per-layer quick checks

- [ ] `file` + `xxd` the first sector — format named
- [ ] `md5sum`/`sha256sum` recorded — provenance
- [ ] Every mount/read flagged read-only
- [ ] part_table/fdisk/mmls — offsets extracted
- [ ] The right fs reader for the volume type
- [ ] `fls -r`/`list --deleted` — both live and deleted seen
- [ ] Deleted entries pulled before carving was assumed needed
- [ ] Unallocated carved; carved files verified to parse
- [ ] NTFS: `-m` listing + named streams checked
- [ ] Slack/swap/hibernate scanned when the rest is dry
- [ ] zip local_only / tar trailer / git dangling checked
- [ ] sqlite freeblock/freelist/-wal/-journal checked
- [ ] Containers (qcow2/vhd/vmdk/dmg/e01) flattened first
- [ ] Firmware fs (cramfs/jffs2/squashfs) walked if embedded
