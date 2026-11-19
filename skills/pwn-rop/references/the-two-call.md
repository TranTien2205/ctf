# The two-call — leak then use


The canonical two-call chain: the first call prints (the leak), the
second uses the computed address — between them, main's re-entry and
the script's arithmetic.
