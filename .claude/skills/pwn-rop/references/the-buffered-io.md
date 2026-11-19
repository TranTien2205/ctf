# Buffered I/O — the recv's reality


TCP delivery is stream-based — a recv may get more or fewer bytes
than the peer sent; buffer and parse, don't assume 1:1 sends:recvs.
