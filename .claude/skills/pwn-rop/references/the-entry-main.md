# Entry and main — the re-entry targets


main's address is the re-entry for two-stage exploits:

    r2 -A ./chal ; afl | grep main
    # or the entry's __libc_start_main call: pdf @ entry0

## The choice

main vs the vuln function: re-enter at the function that re-reaches
the read.
