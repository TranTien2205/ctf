# The count maximum — practical write limits


Writing a large count needs ~N printed bytes: writing 0x7fffffff via one
%n needs ~2GB of output — impractical. Byte-wise %hhn keeps every write
under 255 printed bytes.

## The limit

- A single %n write of value V needs V bytes printed — huge V impractical.
- %hhn writes only count&0xff — each byte needs count ≡ byte (mod 256),
  so ≤255 extra bytes per write.
- 8 %hhn writes, each ≤255 printed bytes → ~2KB for a full address.

## Falsifier

The output cap truncates before the count is reached: the count stops
short; the write value is wrong.
