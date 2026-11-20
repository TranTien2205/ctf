# SubStatus is the answer, Status is generic

Read `SubStatus` first — `0xC0000064` the name does not exist
(enumeration), `0xC000006A` the name exists (password attack),
`0xC0000234` lockout (the `Status`, SubStatus `0x0`). Many 064s over
many names = enumeration; many 06As on one name = password attack.

## The split

064 = name absent; 06A = name exists; 234 = lockout.

## First

SubStatus before Status; 0x0 SubStatus falls back.
