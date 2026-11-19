# Sanitizer strips — when % is filtered


Some inputs pass through a sanitizer that strips or escapes '%' — the
specifiers never reach printf.

## Steps

1. Test: does a sent '%p' reflect as pointer or get stripped?
2. If stripped: find another field, or an encoding that survives.
3. %% produces a literal % — can't bypass a strip filter.

## Falsifier

Every path to a format position filters '%': the class is closed at this
input.
