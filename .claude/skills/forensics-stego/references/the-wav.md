# WAV — the audio channels

WAV stego: LSB of PCM samples, a spectrogram drawing, DTMF tones,
a reversed/slowed track, or a quiet channel.

## The local tools

    python3 tools/forensics/lsb_scan.py f.wav      # PCM LSB matrix
    python3 tools/spectrogram.py f.wav             # freq-domain draw
    python3 tools/dtmf_decode.py f.wav             # touch-tone digits
