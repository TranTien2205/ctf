# Forensics toolbox - identification and quick wins

What to run before the artifact type is decided, plus the lookup tables that
answer most of the small questions.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Quick Start Commands

```bash
# File analysis
file suspicious_file
exiftool suspicious_file     # Metadata
binwalk suspicious_file      # Embedded files
strings -n 8 suspicious_file
hexdump -C suspicious_file | head  # Check magic bytes

# Disk forensics
sudo mount -o loop,ro image.dd /mnt/evidence
fls -r image.dd              # List files
photorec image.dd            # Carve deleted files

# Memory forensics (Volatility 3)
vol3 -f memory.dmp windows.info
vol3 -f memory.dmp windows.pslist
vol3 -f memory.dmp windows.filescan
```

See [disk-and-memory.md](disk-and-memory.md) for full Volatility plugin reference, VM forensics, and coredump analysis.


## Uncommon File Magic Bytes

| Magic | Format | Extension | Notes |
|-------|--------|-----------|-------|
| `OggS` | Ogg container | `.ogg` | Audio/video |
| `RIFF` | RIFF container | `.wav`,`.avi` | Check subformat |
| `%PDF` | PDF | `.pdf` | Check metadata & embedded objects |
| `GCDE` | PrusaSlicer binary G-code | `.g`, `.bgcode` | See 3d-printing.md |


## Common Flag Locations

- PDF metadata fields (Author, Title, Keywords)
- Image EXIF data
- Deleted files (Recycle Bin `$R` files)
- Registry values
- Browser history
- Log file fragments
- Memory strings


## Common Encodings

```bash
echo "base64string" | base64 -d
echo "hexstring" | xxd -r -p
# ROT13: tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

**ROT18:** ROT13 on letters + ROT5 on digits. Common final layer in multi-stage forensics. See [linux-forensics.md](linux-forensics.md) for implementation.

## Additional Technique Quick References

- **Docker image forensics:** Config JSON preserves ALL `RUN` commands even after cleanup. `tar xf app.tar` then inspect config blob. See [linux-forensics.md](linux-forensics.md).
- **Linux attack chains:** Check `auth.log`, `.bash_history`, recent binaries, PCAP. See [linux-forensics.md](linux-forensics.md).
- **RAID 5 XOR recovery:** Two disks of a 3-disk RAID 5 → XOR byte-by-byte to recover the third: `bytes(a ^ b for a, b in zip(disk1, disk3))`. See [disk-advanced.md](disk-advanced.md#raid-5-disk-recovery-via-xor-crypto-cat).
- **GIMP raw memory dump visual inspection:** When Volatility fails, open `.dmp` in GIMP as raw RGB data at monitor width (~1920); scroll to find framebuffer screenshots of user's desktop. See [disk-and-memory.md](disk-and-memory.md#gimp-raw-memory-dump-visual-inspection-inshack-2018).
- **Kyoto Cabinet hash DB forensics:** Recover key ordering from KC hash database with zeroed keys by inserting sequential probe keys and binary-diffing to find which hash slot each overwrites. See [disk-advanced.md](disk-advanced.md#kyoto-cabinet-hash-database-forensics-via-incremental-key-insertion-asis-ctf-2018).
- **PowerShell ransomware:** Extract scripts from minidump, find AES key, decrypt SMTP attachment. See [disk-and-memory.md](disk-and-memory.md).
- **Linux ransomware + memory dump:** If Volatility is unreliable, recover AES key via raw-memory candidate scanning and magic-byte validation; re-extract zip cleanly to avoid missing files/false negatives. See [disk-advanced.md](disk-advanced.md).
- **Deleted partitions:** `testdisk` or `kpartx -av`. See [disk-advanced.md](disk-advanced.md).
- **ZFS forensics:** Reconstruct labels, Fletcher4 checksums, PBKDF2 cracking. See [disk-advanced.md](disk-advanced.md).
- **BSON reconstruction:** Reassemble BSON (Binary JSON) documents from raw bytes; parse with `bson` Python library. See [disk-and-memory.md](disk-and-memory.md#bson-binary-json-format-reconstruction-icectf-2016).
- **TrueCrypt mounting:** Mount TrueCrypt/VeraCrypt volumes with known password using `veracrypt --mount` or `cryptsetup open --type tcrypt`. See [disk-and-memory.md](disk-and-memory.md#truecrypt--veracrypt-volume-mounting-grehack-ctf-2016).
- **Hardware signals:** VGA/HDMI TMDS/DisplayPort, Voyager audio, Saleae UART decode, Flipper Zero. See [signals-and-hardware.md](signals-and-hardware.md).
- **Caps-lock LED Morse from video:** Track caps-lock LED pixel across security camera frames with OpenCV; on/off durations encode Morse code (short=dot, long=dash). See [signals-and-hardware.md](signals-and-hardware.md#caps-lock-led-morse-code-extraction-from-video-stem-ctf-2018).
- **I2C protocol decoding:** Decode I2C bus captures (SDA/SCL lines) to extract data from EEPROM or sensor communications. See [signals-and-hardware.md](signals-and-hardware.md#i2c-bus-protocol-decoding-ekoparty-ctf-2016).
- **Punched card OCR:** Decode IBM-29 punch card images by mapping hole positions to characters using standard encoding grid. See [signals-and-hardware.md](signals-and-hardware.md#ibm-29-punched-card-ocr-ekoparty-ctf-2016).
- **USB HID mouse drawing:** Render relative HID movements per draw mode as bitmap; separate modes, skip pen lifts, scale 5-8x. See [peripheral-capture.md](peripheral-capture.md#usb-hid-mousepen-drawing-recovery-ehax-2026).
- **Side-channel power analysis:** Multi-dimensional power traces (positions × guesses × traces × samples). Average across traces, find sample with max variance, select guess with max power at leak point. See [signals-and-hardware.md](signals-and-hardware.md).
- **Packet interval timing:** Binary data encoded as inter-packet delays in PCAP. Two interval values = two bit values. See [network-advanced.md](network-advanced.md).
- **BMP bitplane QR:** Extract bitplanes 0-2 per RGB channel with NumPy; hidden QR often in bit 1 (not bit 0). See [stego-image.md](stego-image.md#bmp-bitplane-qr-code-extraction--steghide-bypass-ctf-2025).
- **Image puzzle reassembly:** Edge-match pixel differences between piece borders, greedy placement in grid. See [stego-image.md](stego-image.md#image-jigsaw-puzzle-reassembly-via-edge-matching-bypass-ctf-2025).
- **DeepSound audio stego with password cracking:** Extract hash with `deepsound2john.py`, crack with John, retrieve hidden files from WAV; always check both spectrogram and DeepSound. See [stego-advanced.md](stego-advanced.md#deepsound-audio-steganography-with-password-cracking-inshack-2018).
- **QR code reconstruction from curved reflection:** Manually reconstruct QR from glass sphere reflection in video; flip, de-warp, use known plaintext prefix to fix early bytes, high ECC corrects the rest. See [steganography.md](steganography.md#qr-code-reconstruction-from-curved-glass-reflection-in-video-plaidctf-2018).
- **Audio FFT notes:** Dominant frequencies → musical note names (A-G) spell words. See [stego-advanced.md](stego-advanced.md).
- **Audio metadata octal:** Exiftool comment with underscore-separated octal numbers → decode to ASCII/base64. See [stego-advanced.md](stego-advanced.md).
- **G-code visualization:** Side projections (XZ/YZ) reveal text. See [3d-printing.md](3d-printing.md).
- **Git directory recovery:** `gitdumper.sh` for exposed `.git` dirs. See [linux-forensics.md](linux-forensics.md).
- **KeePass v4 cracking:** Standard `keepass2john` lacks v4/Argon2 support; use `ivanmrsulja/keepass2john` fork or `keepass4brute`. Generate wordlists with `cewl`. See [linux-forensics.md](linux-forensics.md).
- **Cross-channel multi-bit LSB:** Different bit positions per RGB channel (R[0], G[1], B[2]) encode hidden data. See [stego-advanced.md](stego-advanced.md).
- **F5 JPEG DCT detection:** Ratio of ±1 to ±2 AC coefficients drops from ~3:1 to ~1:1 with F5; sparse images need secondary ±2/±3 metric. See [stego-image.md](stego-image.md#f5-jpeg-dct-coefficient-ratio-detection-apoorvctf-2026).
- **PNG unused palette stego:** Unused PLTE entries (not referenced by pixels) carry hidden data in red channel values. See [stego-image.md](stego-image.md#png-unused-palette-entry-steganography-apoorvctf-2026).
- **Keyboard acoustic side-channel:** MFCC features from keystroke audio + KNN classification against labeled reference. 10ms window captures impact transient. See [signals-and-hardware.md](signals-and-hardware.md).
- **TCP flag covert channel:** 6 TCP flag bits (FIN/SYN/RST/PSH/ACK/URG) = values 0-63, encoding base64 characters. Nonsensical flag combos on a consistent dest port = covert data. See [network-advanced.md](network-advanced.md).
- **Brotli decompression bomb seam:** Compressed bomb has repeating blocks; flag breaks the pattern at a seam. Compare adjacent blocks to find discontinuity, decompress only that region. See [network-advanced.md](network-advanced.md).
- **Git reflog/fsck squash recovery:** `git rebase --squash` leaves orphaned objects recoverable via `git fsck --unreachable --no-reflogs`. See [linux-forensics.md](linux-forensics.md).
- **DNS trailing byte binary:** Extra bytes (`0x30`/`0x31`) appended after DNS question structure encode binary bits; 8-bit MSB-first chunks → ASCII. See [network-advanced.md](network-advanced.md).
- **Fake TLS + mDNS key + printability merge:** TCP stream disguised as TLS hides ZIP; XOR key from mDNS TXT record; merge two decrypted arrays by selecting printable characters. See [network-advanced.md](network-advanced.md).
- **Seed-based pixel permutation stego:** Deterministic pixel shuffle (Fisher-Yates with known seed) + multi-bitplane interleaved LSB extraction from Y channel → hidden QR code. See [stego-image.md](stego-image.md#seed-based-pixel-permutation--multi-bitplane-qr-l3m0nctf-2025).
- **BTRFS snapshot recovery:** Deleted files persist in BTRFS snapshots/alternate subvolumes. `mount -o subvol=@backup` accesses historical copies. See [disk-recovery.md](disk-recovery.md#btrfs-subvolumesnapshot-recovery-bsidessf-2026).
- **JPEG XL TOC permutation:** JXL's progressive TOC permutation controls tile convergence order during partial decode. Truncate at increasing offsets, measure which tiles converge first → convergence order encodes flag. See [stego-advanced-2.md](stego-advanced-2.md#jpeg-xl-toc-permutation-steganography-bsidessf-2026).
- **Kitty terminal graphics:** `ESC_G` protocol embeds zlib-compressed RGB image data in base64 chunks. Strip escape sequences, concatenate, decompress, reconstruct. See [steganography.md](steganography.md#kitty-terminal-graphics-protocol-decoding-bsidessf-2026).
- **ANSI escape sequence stego:** Flag text interleaved between ANSI color codes and braille characters. Invisible when rendered; extract by stripping escape sequences and non-ASCII. See [steganography.md](steganography.md#ansi-escape-sequence-steganography-in-terminal-art-bsidessf-2026).
- **Autostereogram solving:** Duplicate layer, difference blend, shift horizontally ~100px to reveal hidden 3D text. See [steganography.md](steganography.md#autostereogram--magic-eye-solving-bsidessf-2026).
- **Two-layer byte+line interleaving:** Two files byte-interleaved, then scanlines interleaved. Deinterleave even/odd bytes first (valid images), then even/odd lines. See [steganography.md](steganography.md#two-layer-byteline-interleaving-bsidessf-2026).
- **SMB RID recycling:** Guest auth + LSARPC `LsaLookupSids` with incrementing RIDs enumerates AD accounts from PCAP. See [network-advanced.md](network-advanced.md#smb-rid-recycling-via-lsarpc-midnight-2026).
- **Timeroasting (MS-SNTP):** NTP requests with machine RIDs extract HMAC-MD5 hashes from DC; crack with hashcat -m 31300. See [network-advanced.md](network-advanced.md#timeroasting--ms-sntp-hash-extraction-midnight-2026).
- **Android forensics:** Extract APK with `adb pull`, analyze with `apktool`, check `shared_prefs/` and SQLite databases in `/data/data/<package>/`. See [disk-and-memory.md](disk-and-memory.md#android-forensics).
- **Docker container forensics:** `docker save` exports layered tars; deleted files persist in earlier layers. `docker history --no-trunc` reveals build secrets. See [disk-and-memory.md](disk-and-memory.md#container-forensics-docker).
- **Cloud storage forensics:** S3/GCP/Azure versioning preserves deleted objects. `list-object-versions` recovers deleted flags. See [disk-and-memory.md](disk-and-memory.md#cloud-storage-forensics-aws-s3--gcp--azure).
- **APFS snapshot recovery:** Copy-on-write filesystem preserves historical file states in snapshots; use `icat` with different XID block offsets to read inodes across transaction IDs. See [disk-advanced.md](disk-advanced.md#apfs-snapshot-historical-file-recovery-srdnlenctf-2026).
- **Windows KAPE triage:** Pre-collected artifact ZIPs; start with PowerShell history → Amcache → MFT → registry hives. See [disk-and-memory.md](disk-and-memory.md#windows-kape-triage-analysis-utctf-2026).
- **WordPerfect macro XOR:** `.wcm` files contain macros with embedded encrypted data; XOR formula `(a+b)-2*(a&b)` = bitwise XOR. See [disk-advanced.md](disk-advanced.md#wordperfect-macro-xor-extraction-srdnlenctf-2026).
- **TLS master key from coredump:** Search coredump for session ID (from Wireshark handshake); read 48 bytes before it as master key. Create Wireshark pre-master-secret log file. See [network.md](network.md#tls-master-key-extraction-from-coredump-plaidctf-2014).
- **Corrupted git blob repair:** Single-byte corruption changes SHA-1; brute-force each byte position (256 × file_size) verifying with `git hash-object`. See [linux-forensics.md](linux-forensics.md#corrupted-git-blob-repair-via-byte-brute-force-csaw-ctf-2015).
- **Split archive reassembly from PCAP:** Same-sized HTTP-transferred files with MD5-hash names are archive fragments; order by Apache directory listing timestamps, concatenate, extract password from TCP chat stream. See [network.md](network.md#split-archive-reassembly-from-http-transfers-asis-ctf-finals-2013).
- **Video frame accumulation:** Video with flashing images at various positions; composite all frames (per-pixel maximum) reveals hidden QR code or image. See [stego-advanced-2.md](stego-advanced-2.md#video-frame-accumulation-for-hidden-image-asis-ctf-finals-2013).
- **Reversed audio:** Garbled audio that sounds like speech played backwards; `sox audio.wav reversed.wav reverse` or Audacity Effect → Reverse reveals hidden message. See [stego-advanced-2.md](stego-advanced-2.md#reversed-audio-hidden-message-asis-ctf-finals-2013).
- **Multi-stream video container stego:** MP4/MKV with multiple video streams; default stream is a red herring, flag in secondary stream. `ffprobe -hide_banner file.mp4` to enumerate, `ffmpeg -i file.mp4 -map 0:1 -frames:v 1 flag.jpg` to extract. See [steganography.md](steganography.md#multi-stream-video-container-steganography-bsidessf-2026).
- **FAT16 free space recovery:** Flag hidden in unallocated clusters of FAT16 filesystem. Parse FAT table, enumerate free clusters (entry = 0x0000), read data region. See [disk-recovery.md](disk-recovery.md#fat16-free-space-data-recovery-bsidessf-2026).
- **FAT16 deleted file recovery (fls/icat):** FAT deletion replaces first byte of directory entry with `0xE5` but data remains. `fls -r -d image.img` lists deleted entries, `icat image.img <inode>` recovers by inode. See [disk-recovery.md](disk-recovery.md#fat16-deleted-file-recovery-via-sleuth-kit-metactf-flash-2026).
- **Ext2 orphaned inode recovery:** Deleted file leaves orphaned inode; `e2fsck -y disk.img` reconnects to `/lost+found`. Also use `debugfs` `lsdel` or `icat`. See [disk-recovery.md](disk-recovery.md#ext2-orphaned-inode-recovery-via-fsck-bsidessf-2026).
- **Linux input_event keylogger parsing:** 24-byte `struct input_event` binary dump; filter `type==1` (EV_KEY), `value==1` (press), map keycodes via `input-event-codes.h`. See [signals-and-hardware.md](signals-and-hardware.md#linux-input_event-keylogger-dump-parsing-pwn2win-2016).
- **VBA macro cell data to binary:** Excel cells with numeric values; VBA `CByte((val-78)/3)` transforms to ELF bytes. Reimplement in Python, never run the macro. See [linux-forensics.md](linux-forensics.md#vba-macro-forensics---excel-cell-data-to-elf-binary-sharif-ctf-2016).
- **RGB parity steganography:** Sum R+G+B per pixel; even=white, odd=black renders hidden binary bitmap. See [stego-image.md](stego-image.md#rgb-parity-steganography-break-in-2016).
- **Hidden PDF objects:** Unreferenced content stream objects not in `/Kids` array. Add to `/Kids`, increment `/Count`, re-render. See [network-advanced.md](network-advanced.md#unreferenced-pdf-objects-with-hidden-pages-sharifctf-7-2016).
- **Arnold's Cat Map descrambling:** Periodic chaotic transform on square images; iterate forward map until original reappears. Period divides `3*N`. See [stego-advanced-2.md](stego-advanced-2.md#arnolds-cat-map-image-descrambling-nuit-du-hack-2017).
- **Python in-memory source recovery:** Attach `pyrasite-shell` to running Python process, decompile `func_code` objects with `uncompyle6` (Python <=3.8) or `pycdc` (Python 3.9+), dump `globals()` for secrets. See [linux-forensics.md](linux-forensics.md#python-in-memory-source-recovery-via-pyrasite-insomnihack-2017).
- **HFS+ resource fork recovery:** Hidden data in HFS+ Resource Forks invisible to `binwalk`/`foremost`; use HFSExplorer + 010 Editor HFS template to extract extent records. See [disk-advanced.md](disk-advanced.md#hfs-resource-fork-hidden-binary-recovery-confidence-ctf-2017).
- **Serial UART from WAV audio:** Square wave in audio encodes UART serial data; determine baud rate, parse start/stop bits, decode LSB-first byte frames. See [signals-and-hardware.md](signals-and-hardware.md#serial-uart-data-decoding-from-wav-audio-easyctf-2017).
- **High-resolution SSTV demodulation:** Standard SSTV decoders fail on high-sample-rate recordings; use manual FM demodulation via `arccos` + differentiation. See [stego-advanced-2.md](stego-advanced-2.md#high-resolution-sstv-custom-fm-demodulation-plaidctf-2017).
- **Corrupted ZIP header repair:** Fix filename length fields in both Local File Header (offset 26) and Central Directory (offset 28); fallback: brute-force raw deflate at candidate offsets. See [disk-recovery.md](disk-recovery.md#corrupted-zip-repair-via-header-field-manipulation-plaidctf-2017).
- **SQLite edit history reconstruction:** Replay insert/remove diffs from SQLite diff table to reconstruct document at every intermediate state; flag may have been typed then deleted. See [disk-advanced.md](disk-advanced.md#sqlite-edit-history-reconstruction-from-diff-table-google-ctf-2017).
- **MJPEG FFD9 trailing byte stego:** Extra bytes after JPEG EOI marker (FFD9) in MJPEG frames create invisible covert channel; split on FFD8, extract post-FFD9 data. See [stego-advanced-2.md](stego-advanced-2.md#mjpeg-extra-bytes-after-ffd9-steganography-polictf-2017).
- **USB MIDI Launchpad grid reconstruction:** MIDI Note On/Off in USB PCAP maps to 8x8 Launchpad grid (`key = row*16 + col`); reconstruct visual patterns from button press sequences. See [signals-and-hardware.md](signals-and-hardware.md#usb-midi-launchpad-traffic-reconstruction-sthack-2017).


