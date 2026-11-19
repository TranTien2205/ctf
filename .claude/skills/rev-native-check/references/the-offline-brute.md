# The offline brute — the digest's preimage


When the digest's preimage is small (a charset × a length): brute it
offline — hash each candidate, compare the stored digest:

    for cand in product(alphabet, repeat=n):
        if md5(cand).digest() == stored: found
