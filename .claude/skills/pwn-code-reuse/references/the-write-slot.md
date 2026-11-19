# Choosing the write's slot — the endgame


The write's target is a slot that fires: GOT entry (next call),
function pointer (its call), a chain on the stack (the next ret).

## The firing condition

Every target must be dereferenced after the write — a dead slot is a
dead write.
