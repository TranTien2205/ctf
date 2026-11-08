# Firmware Analysis

## Initial Firmware Triage
```bash
# Identify file type and structure
file firmware.bin
binwalk firmware.bin

# Extract embedded filesystems/files
binwalk -e firmware.bin
binwalk --dd='.*' firmware.bin
```

## Common Firmware Formats
```
Squashfs        # Common compressed read-only filesystem in routers/IoT
JFFS2           # Flash filesystem
UBI/UBIFS       # Another flash filesystem type
CramFS          # Compressed ROM filesystem
U-Boot images   # Bootloader firmware format (uImage)
```

## Extracting Filesystem
```bash
# After binwalk -e, navigate to extracted directory
cd _firmware.bin.extracted/

# If squashfs not auto-extracted
unsquashfs squashfs-root.img

# Mount for exploration (Linux)
sudo mount -t squashfs squashfs-root.img /mnt/fw -o loop
```

## Searching Extracted Filesystem for Secrets
```bash
grep -r "password" _firmware.bin.extracted/
grep -r "BEGIN.*PRIVATE KEY" _firmware.bin.extracted/
find _firmware.bin.extracted/ -name "*.conf" -o -name "*.cfg"
find _firmware.bin.extracted/ -name "passwd" -o -name "shadow"
```

## Identifying Architecture of Binaries
```bash
file _firmware.bin.extracted/bin/*
# ARM, MIPS, or other embedded architectures common in IoT
```

## Emulating Firmware Binaries (QEMU)
```bash
# Install qemu-user-static for cross-architecture emulation
qemu-mipsel-static -L ./squashfs-root ./squashfs-root/bin/busybox

# Full system emulation for network-facing services
# Use firmadyne or FAT (Firmware Analysis Toolkit) for automated setup
```

## Firmware Analysis Toolkit (FAT) / firmadyne Workflow
```bash
# Automated emulation framework for router/IoT firmware
git clone https://github.com/attify/firmware-analysis-toolkit
./fat.py firmware.bin
# Attempts to auto-extract, identify architecture, and emulate network services
```

## Bootloader Analysis (U-Boot)
```bash
# Extract U-Boot image info
mkimage -l uImage

# Check for U-Boot console access via serial (UART) if hardware available
# Often allows interrupting boot to get shell access
```

## Common IoT/Firmware Vulnerabilities to Check
```
- Hardcoded credentials in config files or binaries
- Weak/default admin passwords
- Backdoor accounts in /etc/passwd
- Unencrypted communication (check for TLS usage in binaries)
- Command injection in web management interface (common in routers)
- Buffer overflows in custom network-facing daemons (combine with pwn-binary-triage)
```

## Extracting Certificates/Keys
```bash
find _firmware.bin.extracted/ -name "*.pem" -o -name "*.key" -o -name "*.crt"
openssl x509 -in cert.pem -text -noout
```

## Tools Summary
```
binwalk                    # Extraction and signature scanning
unsquashfs / jefferson      # Filesystem-specific extractors (squashfs/JFFS2)
firmware-mod-kit            # Firmware unpack/repack toolkit
firmadyne / FAT             # Automated emulation frameworks
qemu-user-static             # Cross-architecture binary emulation
Ghidra                       # For analyzing extracted ARM/MIPS binaries
```
