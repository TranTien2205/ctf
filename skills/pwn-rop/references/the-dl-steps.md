# The dl steps — the forge in order


1. Compute the fake reloc index: (fake_rela - .rela.plt) / 24.
2. The fake rela: r_offset=write-target, r_info=(sym_idx<<32)|7.
3. The fake sym: st_name = (fake_str - .dynstr), st_info=0x12.
4. The string: "system" or the target's name.
5. Call: push the index's gadget or the computed plt[0] path.
