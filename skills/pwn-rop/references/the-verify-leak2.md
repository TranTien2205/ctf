# The leak's verify — the three checks


1. Range: pointer-like (0x55/0x7f/0x7ff high bytes).
2. Alignment: the BASE is page-aligned.
3. Distance: two leaks' delta = their offset delta.
