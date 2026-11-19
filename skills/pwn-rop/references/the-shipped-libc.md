# The shipped libc — the exact file


A challenge shipping libc.so.6: every offset is exact — readelf -s
the file; no identification needed.

## The read

    readelf -s libc.so.6 | grep ' system'
    strings -t x libc.so.6 | grep '/bin/sh'
