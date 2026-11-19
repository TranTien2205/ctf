# The dl version check — the verneed dodge


The version walk: the resolver checks DT_VERNEED when st_info's
version flag is set — the fake sym's fields avoid it (st_info=0x12,
no version bit) or the layout places the verneed read on benign
memory.
