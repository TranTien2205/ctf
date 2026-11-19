# Callee-saved registers — the survivors


rbx, rbp, r12-r15 survive calls — values needed after a call live in
them; a chain setting them via the csu tail preserves across the
call.
