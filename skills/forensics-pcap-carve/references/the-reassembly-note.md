# The reassembly note — order, dedup, gaps

## Order

Reassemble in the right order — seq number for a stream, packet
order for a field-carve, the index for indexed chunks.

## Dedup

Retransmissions duplicate bytes — dedup by seq before joining, or
the flag reads doubled.

## Gaps

A lost segment leaves a hole — note it; a "garbled" flag may just
be missing a packet.

## The decode

The reassembled bytes may be hex/base32/base64/xor — decode them;
dns_exfil tries each on a tunnel.

## Verify

The reassembled, deduped, decoded bytes carry the flag — quoted
verbatim, through the hook.
