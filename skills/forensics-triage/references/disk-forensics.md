# Disk Forensics

## Disk Image Formats
```
.dd / .img / .raw     Raw disk image
.E01                   EnCase Expert Witness format
.vmdk                  VMware virtual disk
.vhd/.vhdx             Hyper-V virtual disk
```

## Mounting Disk Images
```bash
# Identify partitions
mmls disk.dd

# Mount raw image (Linux)
sudo mount -o ro,loop,offset=$((512*OFFSET_SECTOR)) disk.dd /mnt/evidence

# Using Autopsy/TSK for structured analysis
fsstat disk.dd
```

## The Sleuth Kit (TSK) Commands
```bash
mmls disk.dd                    # Partition layout
fsstat -o <offset> disk.dd      # Filesystem details
fls -o <offset> disk.dd         # List files (including deleted)
icat -o <offset> disk.dd <inode> > recovered_file  # Extract file by inode
```

## File Recovery (Deleted Files)
```bash
# PhotoRec - recover files by signature scanning regardless of filesystem
photorec disk.dd

# Foremost - similar signature-based carving
foremost -i disk.dd -o output/

# Scalpel - configurable file carving
scalpel disk.dd -o output/

# extundelete for ext3/4
extundelete /dev/sda1 --restore-all
```

## Basic Mount and Explore
```bash
# Linux
mount -o loop,ro challenge.img /mnt/disk
# Windows: Use FTK Imager or dd

# List all files
find /mnt/disk -type f | head -100

# Check for hidden files
ls -la /mnt/disk/

# TestDisk (interactive)
testdisk challenge.img
```

## Timeline Analysis
```bash
# Create timeline from filesystem metadata
fls -r -m / -o <offset> disk.dd > bodyfile.txt
mactime -b bodyfile.txt > timeline.txt

# log2timeline/plaso for comprehensive timeline (multiple artifact types)
log2timeline.py timeline.plaso disk.dd
psort.py -o L2tcsv -w output.csv timeline.plaso
```

## Windows Artifact Analysis
```
$MFT                    Master File Table - file metadata, timestamps
$LogFile                NTFS transaction log
$UsnJrnl                USN Journal - file change history
Prefetch (.pf)          Program execution history
Registry hives          SYSTEM, SOFTWARE, SAM, NTUSER.DAT
Recycle Bin              Deleted file metadata ($I files)
Event Logs (.evtx)       Windows event logs
```

### Registry Analysis Tools
```bash
# RegRipper for automated registry artifact extraction
rip.pl -r SYSTEM -p compname
rip.pl -r NTUSER.DAT -p userassist   # Program execution history
```

### Prefetch Analysis
```bash
# PECmd (Eric Zimmerman tools) for parsing prefetch files
PECmd.exe -f "file.pf"
```

### Event Log Analysis
```bash
# EvtxECmd or python-evtx for parsing .evtx files
python3 -m evtx dump System.evtx > system_events.xml
```

## Filesystem-Specific Notes
```
NTFS       Alternate Data Streams (hidden data), $MFT analysis
ext4       Journal analysis, deleted inode recovery
FAT32      Simpler structure, easier undelete via FAT table analysis
```

## Hash Verification for Evidence Integrity
```bash
md5sum disk.dd
sha256sum disk.dd
# Compare against provided hash to confirm image integrity before analysis
```

## Extracting Specific File Types (Carving by Signature)
```bash
# Foremost config for common types (jpg, pdf, docx, zip)
foremost -t jpg,pdf,zip,doc -i disk.dd -o carved/
```

## Tools Summary
```
Autopsy                # GUI frontend for TSK, comprehensive analysis
The Sleuth Kit (TSK)    # CLI forensics toolkit
PhotoRec/Foremost/Scalpel  # File carving
log2timeline/plaso       # Timeline generation
RegRipper                # Registry artifact extraction
Eric Zimmerman Tools      # Suite of Windows forensics parsers (PECmd, MFTECmd, etc)
```
