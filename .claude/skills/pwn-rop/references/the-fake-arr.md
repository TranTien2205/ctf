# The fake array — argv's shape


execve's argv is an array of pointers ending in NULL — plant
[path_ptr, 0] at a known address and pass THAT address:

    buf: [p64(binsh)][p64(0)]
    rsi = buf
