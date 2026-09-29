# Filesystem and timeline

Answers creation, modification, deletion and ordering questions from NTFS metadata,
and builds the merged timeline that multi-part questions are read from.

The Sleuth Kit 4.12.0 is installed here, so this family is workable today with no
installs. `fls`, `icat`, `istat`, `mmls`, `fsstat`, `blkls`, `mactime`,
`tsk_recover`, `tsk_gettimes`, `img_stat`, `ffind` and `ifind` all resolve.

## Already written here - reference it, do not rewrite it

Four pieces of real DFIR tradecraft already live in this tree. They are correct and
this file defers to them:

| What | Where |
|---|---|
| `$STANDARD_INFORMATION` vs `$FILE_NAME` timestomping detection | `../ctf-forensics/windows.md:294-316` |
| A stdlib-only `USN_RECORD_V2` parser with its reason-flag table | `../ctf-forensics/windows.md:318-354` |
| Alternate data streams and `Zone.Identifier` host URL, extracted with `fls` colon notation | `../ctf-forensics/windows.md:222-292` |
| User profile creation as the first-interactive-logon indicator (`FILE_CREATE`, parent ref 512) | `../ctf-forensics/windows.md:410-423` |
| PowerShell history file write times as a command timeline | `../ctf-forensics/windows.md:394-408` |

The USN parser is the model for anything new written here: stdlib only, no
dependency to install, and it prints a shape that can be recorded as evidence.

## A raw $MFT, standing alone

A bundle that is nothing but a several-hundred-MB `$MFT` asks filesystem questions
only. There are no logs to fall back to.

```bash
ls -l '$MFT'                                  # record the size first
strings -el '$MFT' | grep -i '<name>'         # filenames are UTF-16LE
strings    '$MFT' | grep -i '<name>'          # ASCII, for the occasional resident data
```

Records are 1024 bytes, each beginning with the `FILE` signature. Attribute 0x10 is
`$STANDARD_INFORMATION` (user-modifiable, what most tools show); attribute 0x30 is
`$FILE_NAME` (system-controlled, what proves a timestomp).

Time ordering question with no parser installed: the SI timestamps are what a
question means by "created", unless the question is specifically about
anti-forensics, in which case the SI/FN divergence is the answer.

## A disk image, with a filesystem

```bash
mmls image.dd                                 # partition table, note the offset
fsstat -o <offset> image.dd                   # filesystem type, cluster size
fls -o <offset> -r -p image.dd                # recursive listing with full paths
fls -o <offset> -m C: -r image.dd > bodyfile  # mactime input format
mactime -b bodyfile -d > timeline.csv         # comma-delimited, ready for pandas
icat -o <offset> image.dd <inode> > recovered # extract one file by inode
tsk_recover -o <offset> -e image.dd outdir    # extract everything, including deleted
```

`fls -m C:` plus `mactime -d` is the day-zero timeline path on this box and needs no
install. `-d` gives comma-delimited output; without it `mactime` prints a
human-readable form that does not parse cleanly.

To timeline a whole image in one step: `tsk_gettimes image.dd > bodyfile`.

## Deletion questions

- `$Recycle.Bin\<SID>\$I...` records hold the original path and deletion time; the
  matching `$R...` holds the content. See `../ctf-forensics/windows.md:133-155`.
- A file deleted without the Recycle Bin leaves a `$J` record with reason flag
  `0x200 FILE_DELETE`, and an `$MFT` record whose allocation flag is clear.
- `fls` marks a deleted entry with `*`; the inode is still usable with `icat` until
  the record is reused.

## The merged timeline

Multi-part Sherlock questions ("what happened between X and Y") are read from one
merged, UTC-normalised table, not from four tools side by side.

```python
import pandas

def load(path, **kw):
    df = pandas.read_csv(path, dtype=object, **kw)
    return df

fs  = load("timeline.csv")                       # from mactime -d
evt = load("events.csv")                         # from the EVTX family
net = load("net.csv")                            # from the capture

for df, col in ((fs, "Date"), (evt, "TimeCreated"), (net, "frame.time_epoch")):
    df["ts"] = pandas.to_datetime(df[col], utc=True, errors="coerce")

merged = pandas.concat([
    fs.assign(source="fs"), evt.assign(source="evtx"), net.assign(source="net"),
], ignore_index=True).sort_values("ts")

window = merged[(merged.ts >= "2024-03-06T06:30:00Z") &
                (merged.ts <= "2024-03-06T06:40:00Z")]
```

Three rules that come from being wrong:

- **`utc=True` always.** A mixed-offset column degrades to object dtype and sorts as
  text.
- **`dtype=object` on read.** Without it, hex offsets, SIDs and long account ids are
  coerced to float and the value copied into an answer is wrong in its last digits.
- **`errors="coerce"`, then count the NaT rows.** A parser that emitted a different
  time format silently drops out of the merge otherwise.

For a CSV too large to hold, `pandas.read_csv(..., chunksize=...)` and filter per
chunk before concatenating.

## Why plaso is not used here

`log2timeline` would do all of the above in one command, and it is deliberately not
in the install plan for this box: an apt simulation showed 82 new packages and the
removal of `libafflib0v5`, which is depended on by the installed `sleuthkit` and
would swap it from 4.12.0 to 4.14.0. `mactime` plus pandas covers the same need
without disturbing a working toolchain. If a future bundle genuinely needs a plaso
super-timeline, install it in a container, not on this host.

## Falsifier

This file is the wrong one when the filesystem is intact and uninteresting and the
question is about what a *process* did. That is `windows-event-logs.md`. The
filesystem answers "what changed on disk and when", not "who ran it".
