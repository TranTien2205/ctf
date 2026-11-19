# The ROP workflow — end to end


1. pwn_triage — protections + gadgets + routes.
2. pwn_cyclic — the offset.
3. r2 -A + /R — the gadget set.
4. Decide the ending — by the protections + the imports.
5. Leak if needed — the GOT-print recipe.
6. Build — rop_chain.py's modes or hand-pack.
7. Verify — r2 -d, stage by stage.
8. Fire — socat or a stdlib socket.
9. The flag — the hook.
