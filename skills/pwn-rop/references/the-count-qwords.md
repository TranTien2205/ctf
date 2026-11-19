# Counting qwords — the chain's size


    qwords = len(chain_in_entries)
    bytes = qwords * 8
    total_payload = offset + bytes

## The bound

total_payload <= the read's limit — measure, don't guess.
