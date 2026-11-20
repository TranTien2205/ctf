# The spectrogram — the drawn flag

A flag drawn in the frequency domain is invisible in playback —
spectrogram.py renders the STFT as ASCII (or --png for a pixel
copy); a flat-noise picture closes that channel.

## The call

    python3 tools/spectrogram.py mystery.wav
    python3 tools/spectrogram.py mystery.wav --png out.png
