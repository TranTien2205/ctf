# Chosen-ciphertext access — the second oracle direction — map

| You can | Attack |
|---|---|
| Submit CT and get pad-valid answer | Vaudenay decryption |
| Submit CT and get plaintext | trivial — the flag is free |
| Submit CT and get a validity bit | format/padding oracle |
| Submit CT and get a MAC-valid bit | forgery oracle |

Expanded rows and abort conditions: `chosen-ciphertext.md` and `chosen-ciphertext-deep.md`.
