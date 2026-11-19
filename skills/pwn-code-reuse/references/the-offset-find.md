# Finding the offset — the cyclic way


    python3 tools/pwn_cyclic.py 300 > pat
    # run the binary, feed the pattern, note the rip/rsp at crash
    python3 tools/pwn_cyclic.py --find <rip_value>

The returned offset is the padding length to saved rip.
