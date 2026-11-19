# Worked examples — the numbers for each primitive — checklist



## Checklist

- [ ] Input 'A'*15 → block 0 = 'AAAAAAAAAAAAAAAf'. Save ciphertext block C*.
- [ ] Input 'A'*15 + 'f' → if block 0 == C*, byte 1 = 'f'. Try all 256.
- [ ] Found at guess 102 ('f'). Input 'A'*14 → block 0 = 'AA...AAfl'. Guess 'l'

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
