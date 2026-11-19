# argv[i] — the index into args


main's rsi = argv; argv[i] = [rsi + 8*i + 8] (skipping argv[0]) — the
dereference the compare reads.
