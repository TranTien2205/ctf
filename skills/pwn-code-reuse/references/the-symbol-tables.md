# Symbol tables — nm/readelf for offsets


    nm -D ./chal          # dynamic symbols — the imports
    readelf -s ./chal     # all symbols
    readelf -r ./chal     # the GOT/PLT relocations
    r2 -A ./chal ; afl    # the functions

The offsets every chain entry needs come from these.
