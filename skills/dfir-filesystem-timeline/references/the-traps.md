# The traps

- 0x1000 misread as NAMED_DATA_OVERWRITE (it is RENAME_OLD_NAME;
  NAMED_DATA_OVERWRITE is 0x10).
- `fls -m` eats the next flag as its mandatory prefix.
- Local-time questions vs UTC FILETIMEs.
- $MFT asked for order it cannot prove.
