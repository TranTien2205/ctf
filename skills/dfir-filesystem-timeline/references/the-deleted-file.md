# Deleted-file recovery — three routes

`$J` reason 0x200 + `$MFT` record with the allocation flag clear +
`fls` `*` marker; `icat` extracts until record reuse; `tsk_recover
-e` pulls allocated and unallocated; resident `$DATA` recovers a
small file with no clusters.
