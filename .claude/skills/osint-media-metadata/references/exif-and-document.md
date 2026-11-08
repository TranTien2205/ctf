# Media metadata: EXIF and document properties

The file's own metadata is the first answer — before any reverse-image or
content analysis, read what the file says about itself.

## EXIF on photos

```bash
exiftool photo.jpg          # the whole tag dump
exiftool -GPS* photo.jpg    # just the location fields
```

| Tag | Answers |
|---|---|
| `GPSLatitude`/`GPSLongitude` | where it was taken — the most common CTF win |
| `DateTimeOriginal` | when — correlate with known events |
| `Make`/`Model`/`Software` | the device or the editor that touched it |
| `OwnerName`/`Author`/`Artist` | who |
| `ThumbnailImage` | an embedded earlier version — sometimes unedited |

## Document properties

```bash
exiftool file.pdf doc.docx x.xlsx
```

| Field | Leaks |
|---|---|
| `Author`/`LastModifiedBy` | the username — usually the OS account name |
| `CreateDate`/`ModifyDate` | timeline |
| `Company`/`Manager` | the org |
| embedded fonts/comments | toolchains and annotations |
| OLE streams / revisions | earlier text the file "deleted" |

`docx`/`xlsx` are zip archives — `unzip -l` and read `docProps/` directly for
`core.xml` and `app.xml`; `docProps/custom.xml` carries arbitrary props.

## Stripped or faked metadata

- A platform that re-encodes uploads (Instagram, Twitter) strips EXIF —
  get the *original* from a message, cloud link, or pre-upload mirror.
- `exiftool -all= file` is a known step; CTF files sometimes plant a decoy —
  check the *ThumbnailImage* and revision history for what survived editing.
- `steghide`/`zsteg`/`binwalk` for what metadata can't reach: LSB data,
  appended archives, appended executables.

## The working order

```text
1. file the input          -> what the bytes say they are
2. exiftool (all tags)     -> the metadata dump
3. unzip -l / binwalk      -> what's appended inside
4. reverse-image           -> where else it exists
5. steghide/zsteg          -> the hidden channel, if any
```

## Falsifier

Metadata is genuinely empty — `exiftool` returns only the format defaults,
no GPS, no author, no thumbnail, and binwalk finds nothing appended. The
answer is in the *content* (the picture, the text), not the file.

## Traps

- GPS coordinates need sign + format care (`deg min sec` vs decimal) —
  misread and you're on the wrong continent.
- A "created" timestamp can be the *download* date, not the shoot date —
  compare `DateTimeOriginal` against `CreateDate`.
- Author fields carry machine usernames (`DESKTOP-ABC\user`) — that's the
  pivot, not the answer itself.
