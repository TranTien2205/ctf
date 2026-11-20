# PNG LSB — the bit-plane channel

PNG pixel LSBs carry a hidden stream — zsteg -a sweeps the matrix
(b1-3, rgb channels, xy/yx, lsb/msb); lsb_scan.py is the stdlib
equivalent.

## The local tool

    python3 tools/forensics/lsb_scan.py challenge.png
    python3 tools/forensics/lsb_scan.py challenge.png --planes 1

It walks the same matrix zsteg -a reports and prints every stream
that decodes printable, with a flag-format pass on top.
