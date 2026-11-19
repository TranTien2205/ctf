# The transform shape — xor/permute tables


The input gets transformed (xor, add, rol, a substitution table) then
compared to stored bytes — replicate the transform, or run the
INVERSE on the stored bytes.

## The two answers

- Replicate forward: apply the transform to your guess.
- Invert backward: apply the inverse to the stored constant → the
  correct input directly.
