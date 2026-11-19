# Verifying rip — the overwrite's landing


The first check: does rip land on your first gadget?

    r2 -d ./chal ; dc to the overwrite ; watch rip after the ret

If rip is garbage: the offset is wrong — re-measure.
