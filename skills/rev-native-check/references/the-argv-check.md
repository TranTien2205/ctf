# The argv check — the input via argv


Input via argv[1]: no read call — find the argv access in main's
prologue (rdi=argc, rsi=argv at entry) and follow [rsi+8].
