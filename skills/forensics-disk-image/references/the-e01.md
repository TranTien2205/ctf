# E01 — the EnCase image

ewfmount absent → e01_read.py disk.E01 dump guest.img walks the
chunk table (bit-31 zlib chunks) → flat → part_table chain.
