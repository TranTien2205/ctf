# The static binary — the self-contained check


A static binary: libc's strcmp is a LOCAL function — afl shows it as
fcn.*; the compare's operands still read the same way.
