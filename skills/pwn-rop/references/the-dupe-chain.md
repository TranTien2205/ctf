# The dup chain — redirecting the socket


dup2(sock, 0/1/2) via the chain: redirects stdio to the socket — for
a shell that talks the socket (when the spawn's I/O is elsewhere).

## The shape

    dup2(4, 0); dup2(4, 1); dup2(4, 2); execve("/bin/sh")

— the sockfd (usually 4) per stream.
