# Reading while solving — don't stall the socket

If rounds arrive while a solve runs, the socket buffer fills — recv
only when parsing needs bytes, but keep the buffer across rounds;
a full kernel buffer can stall the server's write and look like a
hang.
