# Steganography Detection & Extraction

## Image Steganography

### Steghide (JPEG/BMP)
```bash
steghide extract -sf image.jpg
steghide extract -sf image.jpg -p ""
steghide info image.jpg
```

### zsteg (PNG/BMP)
```bash
zsteg image.png
zsteg -a image.png
zsteg image.png b1,rgb,lsb
```

### stegsolve
```bash
# GUI tool - check all bit planes
# Analyse > Data Extract
# Analyse > Frame Browser
```

### binwalk
```bash
binwalk -e image.png
binwalk --dd=".*" image.png
```

### exiftool
```bash
exiftool image.jpg
exiftool -Comment image.jpg
exiftool -all= image.jpg  # Remove metadata
```

### strings
```bash
strings image.jpg | grep -iE "flag|ctf|key|password"
strings -n 8 image.jpg
xxd image.jpg | tail -50  # Check appended data
```

### LSB Analysis
```python
from PIL import Image
img = Image.open('image.png')
pixels = img.load()
bits = ''
for y in range(img.height):
    for x in range(img.width):
        r, g, b = pixels[x, y][:3]
        bits += str(r & 1)
        bits += str(g & 1)
        bits += str(b & 1)
# Convert bits to bytes
```

## Audio Steganography
```bash
# Audacity: Spectrogram view
# QSSTV: SSTV signals
# Sonic Visualiser: Layer analysis
```

## Text Steganography
```bash
cat -A file.txt  # Show invisible characters
# Check whitespace steganography
# Check Unicode steganography
```

## Tools Reference
```
steghide        # JPEG/BMP
zsteg            # PNG/BMP
stegsolve        # GUI bit plane analysis
binwalk          # General extraction
exiftool         # Metadata
stegseek         # Steghide brute force
```
