# The csu frame — the extra qwords


After gadget2's call, its epilogue pops 7 registers — the chain must
supply 7 scratch qwords after the csu block before the continuation.
