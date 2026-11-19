# Evidence — what counts

- The recovered bytes of the flag-bearing file/stream/carve.
- The tool + offset + inode/sha/name that produced it.
- The flag through hooks.py pre-flag.

A partition listing or a filename alone is recon.

## The stronger record

- The image's hash (provenance).
- The format + the tool that read it.
- The partition offset, the inode/sha/name.
- The carved region's range and the file's parse check.
- The -wal/-journal/$UsnJrnl frame that carried the deleted row.

## What is NOT evidence

- A magic-byte hit never carved into a parsing file.
- A `fls` name whose data was never read.
- A stream's existence without its bytes.
- A "the flag is probably here" without recovered content.
