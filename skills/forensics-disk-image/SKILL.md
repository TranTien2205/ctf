---
name: forensics-disk-image
description: >
  Action-oriented depth skill for Disk image / filesystem carving. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: forensics-stego, dfir-filesystem-timeline.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [forensics, disk-image, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Disk image / filesystem carving

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

mount or list the filesystem first (fls/icat or mmls) — the flag is usually a deleted file or an unallocated-space carve, not live content

**Falsifier** — the observation that closes this class: live files, deleted entries, and unallocated-space carving all yield only expected OS content
## Recognise

A disk or filesystem image is the handout (`*.dd`, `*.img`, `*.e01`,
partition dumps, ISO) and the flag was deleted, hidden in unallocated space,
or sits in a file the OS pretends is gone.

## Confirm safely

All reads are local. Mount read-only (`-o ro,loop`) or stay in sleuthkit —
never fsck or repair a forensic image. Evidence is the recovered bytes.

## Extraction order

1. `mmls`/`fdisk -l` — the partition table says where data lives and whether
   unallocated space is hiding something.
   No sleuthkit? `python3 tools/forensics/part_table.py image.dd` decodes
   MBR (+EBR logical-chain) or GPT headers itself and emits each
   partition's `first_lba`, `offset` and type as JSON - feed `offset`
   straight into the volume readers below.
2. `fls -r <img>` — live files, including deleted-but-listed entries
   (sleuthkit marks them `*`).
3. `icat <img> <inode>` — pull the deleted entry's bytes before carving.
   No sleuthkit? `python3 tools/forensics/fat_read.py image.img list
   --deleted` walks FAT12/16/32 directories (BPB-derived layout, LFN
   reassembly, `0xE5`-clobbered first char) and `... get /PATH` reads
   the freed cluster chain - the FAT16-deleted-file shape end to end.
   On a whole-disk image pass `--offset` from part_table's `offset`
   field so the volume header lands at byte 0.
   For Linux volumes: `python3 tools/forensics/ext_read.py fs.img ls /`
   walks ext2/3/4 (superblock → GDT → inode tables; both direct-block
   i_block and ext4 extent trees) and `... get /path` reads a file —
   same `--offset` convention. It lists live entries only; deleted
   ext entries need the journal, which is out of scope.
4. `photorec`/`foremost` on unallocated space when `fls` shows nothing —
   carved files keep their magic bytes.
5. Alternate streams and slack: ADS on NTFS (`fls -m`, `icat` named streams),
   `$Extend/$UsnJrnl`, swap.
   Archives inside the image (initramfs cpio, `.a` libraries):
   `python3 tools/forensics/cpio_read.py file list` handles newc cpio
   (070701/070702) and `!<arch>` ar members including `/0` extended
   names; `... get NAME` writes the member to stdout.
   Microsoft `.cab`/`.msu` packages: `python3
   tools/forensics/cab_list.py pack.cab` lists members and folder
   compression; `--extract NAME` recovers uncompressed and MSZIP
   (raw-deflate) folders while LZX/Quantum are named, not guessed.
   Zips: `python3 tools/forensics/zip_struct.py a.zip list` walks LOCAL
   headers and diffs them against the central directory —
   `local_only` names are files present but unregistered (a standard
   hide); `... get NAME` extracts by local header, handling the
   data-descriptor size-in-CD shape.
   `.iso` images: `python3 tools/forensics/iso_read.py cd.iso ls / -r`
   walks the PVD's variable-length directory records recursively and
   `... get /NAME;1` reads the file extent (keep the `;1` version
   suffix — it is part of the on-disc name).
   A `.git` directory: `python3 tools/forensics/git_obj.py ./.git
   dangling` lists loose objects unreachable from refs — the
   flag-in-a-deleted-commit shape — and `... cat <sha>` dumps any
   object body (blob = file content) without the git binary.
   Tarballs: `python3 tools/forensics/tar_tail.py a.tar` lists ustar
   members AND reports bytes appended after the two 512-byte
   end-of-archive blocks — `tar tf` never shows them; `--tail` dumps
   the trailer itself. RAR: `python3 tools/forensics/rar_list.py
   a.rar` walks both header formats (RAR4 fixed fields, RAR5 vint
   headers) — names, packed/unpacked sizes, encrypted flags; it
   reports RAR5-encrypted metadata honestly and never guesses member
   contents.
6. SQLite artifacts (browser history, app dbs, `*.sqlite`): deleted rows
   survive in freeblocks and freelist pages until VACUUM.
   If a `-wal` file sits beside the db, DO NOT open the db — sqlite
   checkpoints the WAL on open and destroys un-checkpointed rows.
   `python3 tools/forensics/sqlite_wal.py db-wal frames` lists frames
   with commit/stale marks, `... strings` scans each page image with
   frame provenance, `... page N` dumps the newest live image.
   Firefox's `*.jsonlz4`/`*.mozlz4` (sessionstore, bookmark backups):
   `python3 tools/forensics/mozlz4.py file` decompresses the
   `mozLz40` block without the lz4 package. A standard framed `.lz4`
   file (magic `04 22 4D 18` — `lz4`-CLI output, firmware blobs):
   `python3 tools/forensics/lz4_frame.py file.lz4 -o out` decodes the
   frame to bytes; `--info` reports the FLG fields it could not
   checksum-verify.
   macOS/iOS property lists (Info.plist, prefs, .mobileconfig):
   `python3 tools/forensics/plist_dump.py file.plist` decodes XML and
   binary plists to JSON; `--key a.b.0` drills one key path.
   `python3 tools/forensics/sqlite_carve.py db.sqlite` emits them as JSON
   (`source=freeblock|unallocated|freelist`); add `--live` to diff against
   live cells. `python3 tools/forensics/browser_hist.py <db>` reads the
   live browser side directly - Chrome `History`/`Cookies`/`Downloads`
   (WebKit-microsecond times) and Firefox `places.sqlite`/`moz_cookies`
   (unix microseconds) detected by schema, visits + downloads + cookies
   as JSON.
   Android `backup.ab` files: `python3 tools/forensics/ab_extract.py b.ab`
   parses the header, inflates the DEFLATE payload, and lists/extracts
   the tar members (`--extract NAME`); AES-256 backups are reported with
   their KDF header rather than guessed at.
   LevelDB stores (Chrome/Chromium IndexedDB `*.log`/`*.ldb`, CTF
   "database dump" handouts): `python3 tools/forensics/leveldb_dump.py
   file` reads WriteBatch `.log` records (deletions listed, not skipped)
   and `.ldb` block tables including raw-snappy blocks — the `snappy`
   module is absent and the decompressor is inline.
   Chromium SimpleCache (`Cache_Data/data_1..3`): `python3
   tools/forensics/chrome_cache.py data_1` walks entries by magic,
   locates bodies through their EOF records, and recovers the URL key
   that the format stores last; `--stream N` dumps one body.
   qcow2 virtual disks (`qemu-img` absent): `python3
   tools/forensics/qcow2_read.py disk.qcow2 dump guest.img` walks the
   L1/L2 tables into a flat image for part_table/fat_read/ext_read;
   `read OFF N` reads guest bytes directly, and compressed clusters
   are counted and named rather than guessed.
7. Office documents carrying VBA (`.doc`, `.xls`, `.xlsm`,
   `vbaProject.bin`): `python3 tools/forensics/vba_extract.py file`
   dumps every module's decompressed source via the CFB container and
   MS-OVBA chunking - oledump without the dependency, for the
   "macro extracts a payload/flag" shape.

`references/deleted-and-unallocated.md` carries the per-tool commands.

## Traps

- Mounting read-write — even by accident — updates access times and can write
  journal entries. `ro` is not optional.
- A `fls` entry marked `*` is deleted-but-allocated: `icat` it before
  assuming carving is needed.
- ext4 zeroes inode block pointers on delete — `fls` shows the name but icat
  gives nothing; carve by signature instead. Record which filesystem you hit.

## Operational probe

```bash
mmls image.dd && fls -r -o <offset> image.dd | grep '\*'
icat -o <offset> image.dd <inode> > recovered
foremost -i image.dd -o carved/
```

## Routing

Shares signals with: `../forensics-stego/`, `../dfir-filesystem-timeline/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/forensics-disk-image/references/README.md`
- `skills/forensics-disk-image/references/deleted-and-unallocated.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
