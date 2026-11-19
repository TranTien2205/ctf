# The fake sections — hand-built structures


A planted region can hold fake structures: a fake Elf64_Rela for
ret2dlresolve, a fake FILE for FSOP, a fake vtable — the bytes the
mechanism reads.
