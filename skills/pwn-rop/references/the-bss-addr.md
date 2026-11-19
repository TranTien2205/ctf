# The .bss address — the writable anchor


    readelf -S ./chal | grep bss

The section's address (non-PIE) is the plant target — /bin/sh, fake
structures, staged chains all land there.
