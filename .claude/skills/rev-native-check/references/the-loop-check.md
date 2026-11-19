# The loop check — the iterated compare


    for i in range(n):
        if transform(input[i]) != expected[i]: fail

The expected[i] source (constant array, computed per-i) is the
extraction target.
