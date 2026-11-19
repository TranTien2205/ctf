# NTFS — the Windows volume

NTFS: $MFT records → attributes ($DATA, $INDEX) — deleted entries,
alternate streams ($DATA:name), slack.

## The streams

`fls -m` + `icat` named streams — an ADS `file:hidden` carries a
second $DATA payload.
