# Smali — the Android assembly

Dalvik/ART is a register machine:

- const/const-string: load a value
- move: copy a register
- invoke-*: call a method
- if-eqz/if-nez/if-eq/if-ne: the deciding branches
- cmp/cmpg: the compare

The if-* after the transform is the decision.
