# tar_tail — the trailer hide

tar members end at two 512-byte zero blocks; bytes appended after
are invisible to `tar tf` — tar_tail.py --tail dumps them.
