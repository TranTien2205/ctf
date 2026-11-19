# The unsorted leak — the heap's libc pointer


A freed large chunk's fd/bk point at main_arena in libc — reading
them (a UAF or a print) is the libc leak's heap route.
