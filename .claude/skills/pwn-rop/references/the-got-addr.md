# The GOT's address — the redirect target


    readelf -r ./chal | grep the_import

The slot's address (non-PIE) is the write target — the import's
resolved-pointer slot.
