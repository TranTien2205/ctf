# Verifying — the produced input


The solve's verify: run the binary with the produced input — the
success branch executes and the flag/answer is observed:

    ./chal < answer.txt
    # or
    echo '<answer>' | ./chal

## The gate

A printed flag goes through hooks.py pre-flag.
