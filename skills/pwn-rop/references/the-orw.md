# The ORW — open/read/write the flag


When no shell exists: open("/flag"), read(fd, buf, n), write(1, buf, n)
— the flag's bytes without execve.

## The chain

    open(path, 0)      # syscall 2, or open@plt
    read(3, buf, 64)   # the new fd
    write(1, buf, 64)

The generic flag-getter when exec is blocked (a sandbox) or no shell
is wanted.
