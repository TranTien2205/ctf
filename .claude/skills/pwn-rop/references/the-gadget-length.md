# Gadget length — the tail's instruction count


A gadget's usable length: instructions until the ret — longer tails
have more side-effect surface.

## The preference

Shortest usable tail first; a long tail's audit cost and side-effect
risk grow with length.
