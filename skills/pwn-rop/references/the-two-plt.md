# plt[0] — the resolver's entry


plt[0] (the first PLT entry) does push [got+8]; jmp [got+16] — the
link_map pointer and the resolver — the forge's entry point.
