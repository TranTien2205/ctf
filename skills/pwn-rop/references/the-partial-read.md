# Partial reads — the fragmented recv


A recv may return part of the output — loop until the expected bytes
or a delimiter arrives; the leak's bytes must be complete before
unpacking.
