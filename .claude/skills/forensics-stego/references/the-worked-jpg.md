# Worked — a JPEG steghide

1. file/exiftool → real JPEG.
2. A recovered word from the challenge is the passphrase.
3. steghide extract -sf photo.jpg -p 'word' → the flag.
