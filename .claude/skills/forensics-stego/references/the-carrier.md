# Identify the carrier first

The carrier IS the routing: a PNG's channel is bit-planes; a JPEG's
is DCT coefficients or steghide; a WAV's is PCM samples or
spectrogram; a container's is appended data.

## The read

    file challenge.png
    xxd challenge.png | head     # the magic, not the extension

`file` reporting 'data' means a renamed container — the magic bytes
tell the real format.
