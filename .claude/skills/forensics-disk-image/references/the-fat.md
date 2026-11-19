# FAT12/16/32 — the volume read

FAT volumes: BPB → FAT → root/data dirs — the deleted file's first
char is 0xE5-clobbered but the cluster chain still reads.

## The tool

    python3 tools/forensics/fat_read.py image.img list --deleted
    python3 tools/forensics/fat_read.py image.img get /PATH
    python3 tools/forensics/fat_read.py image.img list --offset N
