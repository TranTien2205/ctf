# The traps

- rw mount destroys journal/atime.
- ext4 zeroes inode block ptrs on delete — carve by signature.
- A -wal opened destroys un-checkpointed rows.
- A fragmented carve is incomplete.
- `fls *` shows the name; the data may be gone.

## More traps

- A zip's `local_only` member is invisible to a central-directory
  listing — zip_struct's diff finds it.
- A tar's post-EOT bytes are invisible to `tar tf` — tar_tail.
- A .git's dangling object is invisible to `git log` — git_obj.
- A sqlite -wal opened destroys un-checkpointed rows — read the
  -wal/-journal directly, never the db.
- A high-entropy region is encrypted or compressed — enc_detect
  names it; don't mistake it for a wipe.
- A carved file that doesn't parse is a false magic — verify it.
- A fragmented file carves incomplete — a partial carve isn't the
  whole file.
- A quick-formatted volume still holds the data — don't assume the
  format erased it.
- A differencing/snapshot disk reads through the parent — a delta
  alone is incomplete.
- ext4 delete zeroes the inode's block pointers — the name lists,
  icat returns nothing; carve by signature.
- A LUKS/BitLocker region is encrypted, not corrupt — name the
  cipher, don't force it.
- A "flag.txt" is a decoy until the content is verified.
