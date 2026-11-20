# JPEG — steghide and DCT

JPEG stego: steghide (passphrase-protected embeds), outguess, or
DCT-coefficient hides — steghide needs a passphrase, often a string
recovered earlier.

## The try

    steghide extract -sf photo.jpg -p 'word'

Try recovered words before brute force — the passphrase is often a
string found earlier in the challenge.
