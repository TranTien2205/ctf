# The length check — the first gate


Often a length check precedes the content check — strlen(input) == N
or a bounds compare — it fixes the input's size, a useful constraint.

## The use

The required length narrows the brute force and confirms the check's
domain.
