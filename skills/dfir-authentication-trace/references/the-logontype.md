# LogonType decides the fields — read it first

`LogonType` 3 is not RDP (10, or 12 cached); 4 batch, 5 service,
7 unlock, 9 NewCredentials, 11 cached. A type 3 from the same
address at the same minute is the share/pipe side of the visit.

## First read

The type decides what every other field means.

## Not RDP

3 is the share/pipe side; 10/12 is RDP.
