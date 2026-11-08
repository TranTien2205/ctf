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
2. `fls -r <img>` — live files, including deleted-but-listed entries
   (sleuthkit marks them `*`).
3. `icat <img> <inode>` — pull the deleted entry's bytes before carving.
4. `photorec`/`foremost` on unallocated space when `fls` shows nothing —
   carved files keep their magic bytes.
5. Alternate streams and slack: ADS on NTFS (`fls -m`, `icat` named streams),
   `$Extend/$UsnJrnl`, swap.
6. SQLite artifacts (browser history, app dbs, `*.sqlite`): deleted rows
   survive in freeblocks and freelist pages until VACUUM.
   `python3 tools/forensics/sqlite_carve.py db.sqlite` emits them as JSON
   (`source=freeblock|unallocated|freelist`); add `--live` to diff against
   live cells.

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
