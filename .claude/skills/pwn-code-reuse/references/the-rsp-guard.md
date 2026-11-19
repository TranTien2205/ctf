# rsp guard — keeping the walk clean


The chain consumes stack qwords; running out of them (the buffer's
end) walks rsp into unmapped memory — the chain must fit the buffer,
or a pivot extends it.
