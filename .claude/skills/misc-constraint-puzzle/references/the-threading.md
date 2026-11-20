# Threads — rarely the answer

One socket, sequential rounds — a worker thread only helps if the
solve itself is parallel; the socket is not the bottleneck.

## Rarely

One socket — threads only for a parallel solve.

## Rarely

The socket isn't the bottleneck.
