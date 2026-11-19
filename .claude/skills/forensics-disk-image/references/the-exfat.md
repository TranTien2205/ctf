# exFAT — the USB/SD volume

exFAT: VBR → FAT chain or contiguous stream flag → entry sets —
the deleted set's type-byte high bit clears.

## The tool

    python3 tools/forensics/exfat_read.py image.img list
    python3 tools/forensics/exfat_read.py image.img get /PATH
    # --offset for a whole-disk image
