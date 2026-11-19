# The first gadget — the landing check


The chain's first entry must be where rip lands — verify the ret that
overwrites reaches it: the offset's slot + the first qword = the
first gadget.
