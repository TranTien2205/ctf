# Keeping rsp sane — the walk's integrity


The ret-walk consumes qwords — the chain must keep feeding valid
entries or rsp walks into unmapped/garbage: the chain's length IS
the payload length past the offset.

## The bound

The chain's length is bounded by the read's limit — count the qwords.
