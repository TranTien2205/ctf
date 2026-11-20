# DTMF — the touch-tone digits

A WAV of phone dial tones decodes to digits — dtmf_decode.py runs a
Goertzel power estimate over the eight DTMF frequencies into the
digit string.

## The call

    python3 tools/dtmf_decode.py dial.wav
    python3 tools/dtmf_decode.py dial.wav --frames   # per-window pair
